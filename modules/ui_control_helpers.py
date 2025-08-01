import os
import gradio as gr
from PIL import Image
from modules import shared, scripts_manager, masking, video # pylint: disable=ungrouped-imports


gr_height = None
max_units = shared.opts.control_max_units
debug = os.environ.get('SD_CONTROL_DEBUG', None) is not None
debug_log = shared.log.trace if debug else lambda *args, **kwargs: None

# state variables
busy = False # used to synchronize select_input and generate_click
input_source = None
input_init = None
input_mask = None


def initialize():
    from modules import devices
    from modules.control import unit
    from modules.control import processors # patrickvonplaten controlnet_aux
    from modules.control.units import controlnet # lllyasviel ControlNet
    from modules.control.units import xs # vislearn ControlNet-XS
    from modules.control.units import lite # vislearn ControlNet-XS
    from modules.control.units import t2iadapter # TencentARC T2I-Adapter
    shared.log.debug(f'UI initialize: control models="{shared.opts.control_dir}"')
    controlnet.cache_dir = os.path.join(shared.opts.control_dir, 'controlnet')
    xs.cache_dir = os.path.join(shared.opts.control_dir, 'xs')
    lite.cache_dir = os.path.join(shared.opts.control_dir, 'lite')
    t2iadapter.cache_dir = os.path.join(shared.opts.control_dir, 'adapter')
    processors.cache_dir = os.path.join(shared.opts.control_dir, 'processor')
    masking.cache_dir = os.path.join(shared.opts.control_dir, 'segment')
    unit.default_device = devices.device
    unit.default_dtype = devices.dtype
    try:
        os.makedirs(shared.opts.control_dir, exist_ok=True)
        os.makedirs(controlnet.cache_dir, exist_ok=True)
        os.makedirs(xs.cache_dir, exist_ok=True)
        os.makedirs(lite.cache_dir, exist_ok=True)
        os.makedirs(t2iadapter.cache_dir, exist_ok=True)
        os.makedirs(processors.cache_dir, exist_ok=True)
        os.makedirs(masking.cache_dir, exist_ok=True)
    except Exception:
        pass
    scripts_manager.scripts_current = scripts_manager.scripts_control
    scripts_manager.scripts_control.initialize_scripts(is_img2img=False, is_control=True)


def interrogate():
    prompt = None
    try:
        from modules.interrogate.interrogate import interrogate as interrogate_fn
        prompt = interrogate_fn(input_source[0])
    except Exception:
        pass
    return prompt


def display_units(num_units):
    num_units = num_units or 1
    return (num_units * [gr.update(visible=True)]) + ((max_units - num_units) * [gr.update(visible=False)])


def get_video(filepath: str):
    try:
        frames, fps, duration, w, h, codec, _cap = video.get_video_params(filepath)
        shared.log.debug(f'Control: input video: path={filepath} frames={frames} fps={fps} size={w}x{h} codec={codec}')
        msg = f'Control input | Video | Size {w}x{h} | Frames {frames} | FPS {fps:.2f} | Duration {duration:.2f} | Codec {codec}'
        return msg
    except Exception as e:
        msg = f'Control: video open failed: path={filepath} {e}'
        shared.log.error(msg)
        return msg


def select_input(input_mode, input_image, init_image, init_type, input_resize, input_inpaint, input_video, input_batch, input_folder):
    global busy, input_source, input_init, input_mask # pylint: disable=global-statement
    busy = True
    if input_mode == 'Select':
        selected_input = input_image
    elif input_mode == 'Outpaint':
        selected_input = input_resize
    elif input_mode == 'Inpaint':
        selected_input = input_inpaint
    elif input_mode == 'Video':
        selected_input = input_video
    elif input_mode == 'Batch':
        selected_input = input_batch
    elif input_mode == 'Folder':
        selected_input = input_folder
    else:
        selected_input = None
    size = [gr.update(), gr.update()]
    if selected_input is None:
        input_source = None
        busy = False
        # debug('Control input: none')
        return [gr.Tabs.update(), None, ''] + size
    input_type = type(selected_input)
    input_mask = None
    status = 'Control input | Unknown'
    res = [gr.Tabs.update(selected='out-gallery'), input_mask, status]
    # control inputs
    if isinstance(selected_input, Image.Image): # image via upload -> image
        if input_mode == 'Outpaint':
            masking.opts.invert = True
            selected_input, input_mask = masking.outpaint(input_image=selected_input)
        input_source = [selected_input]
        input_type = 'PIL.Image'
        status = f'Control input | Image | Size {selected_input.width}x{selected_input.height} | Mode {selected_input.mode}'
        size = [gr.update(value=selected_input.width), gr.update(value=selected_input.height)]
        res = [gr.Tabs.update(selected='out-gallery'), input_mask, status]
    elif isinstance(selected_input, dict): # inpaint -> dict image+mask
        input_mask = selected_input['mask']
        selected_input = selected_input['image']
        input_source = [selected_input]
        input_type = 'PIL.Image'
        status = f'Control input | Image | Size {selected_input.width}x{selected_input.height} | Mode {selected_input.mode}'
        res = [gr.Tabs.update(selected='out-gallery'), input_mask, status]
    elif isinstance(selected_input, gr.components.image.Image): # not likely
        input_source = [selected_input.value]
        input_type = 'gr.Image'
        res = [gr.Tabs.update(selected='out-gallery'), input_mask, status]
    elif isinstance(selected_input, str): # video via upload > tmp filepath to video
        input_source = selected_input
        input_type = 'gr.Video'
        status = get_video(input_source)
        res = [gr.Tabs.update(selected='out-video'), input_mask, status]
    elif isinstance(selected_input, list): # batch or folder via upload -> list of tmp filepaths
        if hasattr(selected_input[0], 'name'):
            input_type = 'tempfiles'
            input_source = [f.name for f in selected_input] # tempfile
        else:
            input_type = 'files'
            input_source = selected_input
        status = f'Control input | Images | Files {len(input_source)}'
        res = [gr.Tabs.update(selected='out-gallery'), input_mask, status]
    else: # unknown
        input_source = None
    # init inputs: optional
    if init_type == 0: # Control only
        input_init = None
    elif init_type == 1: # Init image same as control assigned during runtime
        input_init = None
    elif init_type == 2: # Separate init image
        input_init = [init_image]
    debug_log(f'Control select input: type={input_type} source={input_source} init={input_init} mask={input_mask} mode={input_mode}')
    busy = False
    return res + size


def copy_input(mode_from, mode_to, input_image, input_resize, input_inpaint):
    debug_log(f'Control transfter input: from={mode_from} to={mode_to} image={input_image} resize={input_resize} inpaint={input_inpaint}')
    def getimg(ctrl):
        if ctrl is None:
            return None
        return ctrl.get('image', None) if isinstance(ctrl, dict) else ctrl

    if mode_from == mode_to:
        return [gr.update(), gr.update(), gr.update()]
    elif mode_to == 'Select':
        return [getimg(input_resize) if mode_from == 'Outpaint' else getimg(input_inpaint), None, None]
    elif mode_to == 'Inpaint':
        return [None, None, getimg(input_image) if mode_from == 'Select' else getimg(input_resize)]
    elif mode_to == 'Outpaint':
        return [None, getimg(input_image) if mode_from == 'Select' else getimg(input_inpaint), None]
    else:
        shared.log.error(f'Control transfer unknown input: from={mode_from} to={mode_to}')
        return [gr.update(), gr.update(), gr.update()]


def transfer_input(dst):
    return [gr.update(visible=dst=='Select'), gr.update(visible=dst=='Outpaint'), gr.update(visible=dst=='Inpaint'), gr.update(interactive=dst!='Select'), gr.update(interactive=dst!='Inpaint'), gr.update(interactive=dst!='Outpaint')]
