from modules import scripts_manager, scripts_postprocessing, shared


class ScriptPostprocessingForMainUI(scripts_manager.Script):
    def __init__(self, script_postproc):
        self.script: scripts_postprocessing.ScriptPostprocessing = script_postproc
        self.postprocessing_controls = None

    def title(self):
        return self.script.name

    def show(self, is_img2img): # pylint: disable=unused-argument
        return scripts_manager.AlwaysVisible

    def ui(self, is_img2img): # pylint: disable=unused-argument
        self.postprocessing_controls = self.script.ui()
        return self.postprocessing_controls.values()

    def postprocess_image(self, p, script_pp, *args): # pylint: disable=arguments-differ
        args_dict = dict(zip(self.postprocessing_controls, args))
        pp = scripts_postprocessing.PostprocessedImage(script_pp.image)
        pp.info = {}
        self.script.process(pp, **args_dict)
        p.extra_generation_params.update(pp.info)
        script_pp.image = pp.image


def create_auto_preprocessing_script_data():
    res = []
    for name in shared.opts.postprocessing_enable_in_main_ui:
        script = next(iter([x for x in scripts_manager.postprocessing_scripts_data if x.script_class.name == name]), None)
        if script is None:
            continue
        constructor = lambda s=script: ScriptPostprocessingForMainUI(s.script_class()) # pylint: disable=unnecessary-lambda-assignment
        res.append(scripts_manager.ScriptClassData(script_class=constructor, path=script.path, basedir=script.basedir, module=script.module))
    return res
