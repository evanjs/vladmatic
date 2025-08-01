# TODO

Main ToDo list can be found at [GitHub projects](https://github.com/users/vladmandic/projects)

## Current

- Gallery: force refresh on delete

## Future Candidates

- [Modular pipelines and guiders](https://github.com/huggingface/diffusers/issues/11915)  
- Refactor: Sampler options  
- Feature: Diffusers [group offloading](https://github.com/vladmandic/sdnext/issues/4049)  
- Feature: Common repo for `T5` and `CLiP`  
- Feature: LoRA add OMI format support for SD35/FLUX.1  
- Video: Generic API support  
- Video: LTX TeaCache and others  
- Video: LTX API  
- Video: LTX PromptEnhance
- Video: LTX Conditioning preprocess
- [WanAI-2.1 VACE](https://huggingface.co/Wan-AI/Wan2.1-VACE-14B)(https://github.com/huggingface/diffusers/pull/11582)  
- [SkyReels-v2](https://github.com/SkyworkAI/SkyReels-V2)(https://github.com/huggingface/diffusers/pull/11518)  
- [Cosmos-Predict2-Video](https://huggingface.co/nvidia/Cosmos-Predict2-2B-Video2World)(https://github.com/huggingface/diffusers/pull/11695)  

### Blocked items

- Upgrade: unblock `pydantic` and `albumentations`
  - see <https://github.com/Cschlaefli/automatic>
  - blocked by `insightface`

## ModernUI

- Extensions tab:
  - full CSS redesign
- Models tab: 
  - Validate subtab: replace table with custom html
  - Update subtab: replace table with custom html
  - CivitAI subtab: redesign downloader

### Under Consideration

- [IPAdapter negative guidance](https://github.com/huggingface/diffusers/discussions/7167)  
- [IPAdapter composition](https://huggingface.co/ostris/ip-composition-adapter)  
- [STG](https://github.com/huggingface/diffusers/blob/main/examples/community/README.md#spatiotemporal-skip-guidance)  
- [SmoothCache](https://github.com/huggingface/diffusers/issues/11135)  
- [MagCache](https://github.com/lllyasviel/FramePack/pull/673/files)
- [HiDream GGUF](https://github.com/huggingface/diffusers/pull/11550)  
- [Nunchaku PulID](https://github.com/mit-han-lab/nunchaku/pull/274)  
- [Dream0 guidance](https://huggingface.co/ByteDance/DreamO)  
- [SUPIR upscaler](https://github.com/Fanghua-Yu/SUPIR)  
- Remove: Agent Scheduler  
- Remove: CodeFormer  
- Remove: GFPGAN  
- ModernUI: Lite vs Expert mode  
- [Canvas](https://konvajs.org/)  

### Future Considerations
- [TensorRT](https://github.com/huggingface/diffusers/pull/11173)  

### New models

#### Pending
- [Magi](https://github.com/SandAI-org/MAGI-1)(https://github.com/huggingface/diffusers/pull/11713)  
- [SEVA](https://github.com/huggingface/diffusers/pull/11440)  
#### External:Unified/MultiModal
- [Ming](https://github.com/inclusionAI/Ming)  
- [Liquid](https://github.com/FoundationVision/Liquid)  
#### External:Image2Image/Editing
- [Step1X](https://github.com/stepfun-ai/Step1X-Edit)  
- [SD3 UltraEdit](https://github.com/HaozheZhao/UltraEdit)  
#### External:Video
- [WAN2GP](https://github.com/deepbeepmeep/Wan2GP)  
- [SelfForcing](https://github.com/guandeh17/Self-Forcing)  
- [DiffusionForcing](https://github.com/kwsong0113/diffusion-forcing-transformer)  
- [LanDiff](https://github.com/landiff/landiff)  
- [HunyuanCustom](https://github.com/Tencent-Hunyuan/HunyuanCustom)  
- [HunyuanAvatar](https://huggingface.co/tencent/HunyuanVideo-Avatar)  
- [WAN-CausVid](https://huggingface.co/lightx2v/Wan2.1-T2V-14B-CausVid)  
- [WAN-CausVid-Plus t2v](https://github.com/goatWu/CausVid-Plus/)  
- [WAN-StepDistill](https://huggingface.co/lightx2v/Wan2.1-T2V-14B-StepDistill-CfgDistill)  

## Code TODO

> pnpm lint | grep W0511 | awk -F'TODO ' '{print "- "$NF}' | sed 's/ (fixme)//g' | sort
 
- control: support scripts via api
- fc: autodetect distilled based on model
- fc: autodetect tensor format based on model
- flux: loader for civitai nf4 models
- hypertile: vae breaks when using non-standard sizes
- install: enable ROCm for windows when available
- loader: load receipe
- loader: save receipe
- lora: add other quantization types
- lora: add t5 key support for sd35/f1
- lora: maybe force imediate quantization
- lora: support pre-quantized flux
- model load: cogview4: balanced offload does not work for GlmModel
- model load: add ChromaFillPipeline, ChromaControlPipeline, ChromaImg2ImgPipeline etc when available
- model load: force-reloading entire model as loading transformers only leads to massive memory usage
- model load: implement model in-memory caching
- modernui: monkey-patch for missing tabs.select event
- processing: remove duplicate mask params
- resize image: enable full VAE mode for resize-latent
