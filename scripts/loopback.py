import math

import gradio as gr
from modules import images, processing, scripts_manager
from modules.processing import Processed
from modules.shared import opts, state, log


class Script(scripts_manager.Script):
    def title(self):
        return "Loopback"

    def show(self, is_img2img):
        return True

    def ui(self, is_img2img):
        with gr.Row():
            gr.HTML("<span>&nbsp Loopback</span><br>")
        with gr.Row():
            loops = gr.Slider(minimum=1, maximum=32, step=1, label='Loops', value=2, elem_id=self.elem_id("loops"))
            final_denoising_strength = gr.Slider(minimum=0, maximum=1, step=0.01, label='Final strength', value=0.5, elem_id=self.elem_id("final_denoising_strength"))
        with gr.Row():
            denoising_curve = gr.Dropdown(label="Strength curve", choices=["Aggressive", "Linear", "Lazy"], value="Linear")

        return [loops, final_denoising_strength, denoising_curve]

    def run(self, p, loops, final_denoising_strength, denoising_curve): # pylint: disable=arguments-differ
        processing.fix_seed(p)
        initial_batch_count = p.n_iter
        p.extra_generation_params['Loopback'] = final_denoising_strength
        p.batch_size = 1
        p.n_iter = 1
        info = None
        initial_seed = None
        initial_info = None
        initial_denoising_strength = p.denoising_strength
        initial_color_corrections = [processing.setup_color_correction(p.init_images[0])] if p.init_images is not None and len(p.init_images) > 0 else None
        grids = []
        all_images = []
        initial_init_images = p.init_images
        original_inpainting_fill = p.inpainting_fill
        state.job_count = loops * initial_batch_count
        history = []

        def calculate_denoising_strength(loop):
            strength = initial_denoising_strength
            if loops == 1:
                return strength
            progress = loop / (loops - 1)
            if denoising_curve == "Aggressive":
                strength = math.sin((progress) * math.pi * 0.5)
            elif denoising_curve == "Lazy":
                strength = 1 - math.cos((progress) * math.pi * 0.5)
            else:
                strength = progress
            change = (final_denoising_strength - initial_denoising_strength) * strength
            return initial_denoising_strength + change

        for n in range(initial_batch_count):
            p.init_images = initial_init_images
            p.denoising_strength = initial_denoising_strength
            last_image = None

            for i in range(loops):
                p.n_iter = 1
                p.batch_size = 1
                p.do_not_save_grid = True
                if opts.img2img_color_correction:
                    p.color_corrections = initial_color_corrections
                state.job = f"loopback iteration {i+1}/{loops} batch {n+1}/{initial_batch_count}"
                processed = processing.process_images(p)
                if processed is None:
                    log.error("Loopback: processing output is none")
                    return Processed(p, [], None, None)
                if state.interrupted or state.skipped:
                    break
                if initial_seed is None:
                    initial_seed = processed.seed
                    initial_info = processed.info
                p.seed = processed.seed + 1 # why?
                p.denoising_strength = calculate_denoising_strength(i + 1)
                last_image = processed.images[0]
                p.init_images = [last_image]
                if initial_batch_count == 1:
                    history.append(last_image)
                    all_images.append(last_image)

            if (initial_batch_count > 1) and (not state.skipped) and (not state.interrupted):
                history.append(last_image)
                all_images.append(last_image)
            p.inpainting_fill = original_inpainting_fill
            if state.interrupted:
                break

        if len(history) > 1:
            grid = images.image_grid(history, rows=1)
            if opts.grid_save:
                images.save_image(grid, p.outpath_grids, "grid", initial_seed, p.prompt, opts.grid_format, info=info, grid=True, p=p)
            if opts.return_grid:
                grids.append(grid)
        all_images = grids + all_images
        processed = Processed(p, all_images, initial_seed, initial_info)
        return processed
