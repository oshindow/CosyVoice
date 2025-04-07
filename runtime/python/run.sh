      
#!/bin/sh
docker run \
    --gpus '"device=0"' \
    -itd \
    -v /data/codes/CosyVoice/pretrained_models:/opt/CosyVoice/pretrained_models \
    -p 8080:8080 \
    -p 50000:50000 \
    --name cosyvoice \
    cosyvoice:v1.0 \
    /bin/bash -c "
    cd /opt/CosyVoice/CosyVoice/runtime/python/grpc && \
    (GRPC_SERVER=localhost:50000 python -m uvicorn app:app --host 0.0.0.0 --port 8080 &) && \
    python3 server_stream.py --port 50000 --model_dir /opt/CosyVoice/pretrained_models/CosyVoice-300M-Instruct
    "

# docker run \
#     --gpus all \
#     -v /data/codes/CosyVoice/pretrained_models:/opt/CosyVoice/pretrained_models \
#     -p 50000:50000 \
#     -it \
#     cosyvoice:v1.0 /bin/bash
# NETWORK_NAME="mii_network"
# if ! docker network ls | grep -q "$NETWORK_NAME"; then
#     echo "Network '$NETWORK_NAME' does not exist, creating..."
#     exit
# fi

# HOST_IP=$(docker network inspect bridge | grep -m 1 Gateway | awk -F '"' '{print $4}')
# # 检查 HOST_IP 是否是有效的 IP 地址
# if [[ ! $HOST_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
#     echo "通过docker network inspect bridge读取hostip失败"
#     echo "尝试使用ifconfig读取docker0获取..."
#     HOST_IP=$(ifconfig docker0 | grep "inet " | awk '{print $2}')
#     if [[ ! $HOST_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
#         echo "通过ifconfig docker0读取hostip失败"
#         echo "尝试使用ip addr读取docker0获取..."
#         HOST_IP=$(ip addr show docker0 | grep "inet\b" | awk '{print $2}' | cut -d/ -f1)
#         if [[ ! $HOST_IP =~ ^[0-9]+\.[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
#             echo "通过ip addr docker0读取hostip失败"
#             echo "直接退出"
#             exit
#         fi
#     fi
# fi

# container_name="mii-tritonserver"
# image_name="image_name_place:image_version_place"
# root_dir="/data/docker/tritonserver"

# # 检查特定镜像和版本是否存在
# docker image inspect "${image_name}" >/dev/null 2>&1

# # $? 是上一个命令的退出状态码
# if [ $? -eq 0 ]; then
#     echo "镜像 '${image_name}' 存在，继续启动容器..."
# else
#     echo "镜像 '${image_name}' 不存在，退出脚本。"
#     exit 1
# fi

# # 停止container
# stop_res=$(docker stop $container_name | grep "Error")
# if [[ "$stop_res" != "" ]]; then
#     echo $stop_res
#     exit
# fi

# # 删除container
# rm_res=$(docker rm $container_name | grep "Error")
# if [[ "$rm_res" != "" ]]; then
#     echo $rm_res
#     exit
# fi

# cp -rf ../configs $root_dir

# docker run --add-host=host.docker.internal:$HOST_IP \
#     --name $container_name \
#     --restart=always \
#     --network $NETWORK_NAME \
#     --gpus all \
#     --log-driver=json-file --log-opt max-size=1g --log-opt max-file=2 \
#     -p 6001:8001 \
#     -p 6002:8002 \
#     -v $root_dir/models:/workspace/models \
#     -v $root_dir/configs/start-tritonserver.sh:/usr/sbin/start-tritonserver.sh \
#     --shm-size=4g \
#     -d \
#     $image_name

# docker logs -f $container_name

    