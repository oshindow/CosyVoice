# python3 cosyvoice/bin/export_onnx.py
trtexec --onnx=pretrained_models/CosyVoice-300M-Instruct/flow.decoder.estimator.fp32.4090.onnx \
    --saveEngine=pretrained_models/CosyVoice-300M-Instruct/flow.decoder.estimator.fp32.4090.plan \
    --minShapes=x:1x80x1,mask:1x1x1,mu:1x80x1,cond:1x80x1,t:1,spks:1x80 \
    --optShapes=x:3x80x256,mask:3x1x256,mu:3x80x256,cond:3x80x256,t:3,spks:3x80 \
    --maxShapes=x:4x80x2000,mask:4x1x2000,mu:4x80x2000,cond:4x80x2000,t:4,spks:4x80 \
    # --fp16