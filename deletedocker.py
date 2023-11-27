import docker

def remove_docker_image_by_name(image_name):
    try:
        # 创建 Docker 客户端对象
        client = docker.from_env()

        # 查找指定名称的 Docker 镜像
        image = client.images.get(image_name)

        if image:
            print(f"Removing Docker image '{image_name}'...")
            # 删除镜像
            client.images.remove(image.id, force=True)
            print(f"Docker image '{image_name}' removed successfully.")
        else:
            print(f"Docker image '{image_name}' not found.")
    except docker.errors.ImageNotFound:
        print(f"Docker image '{image_name}' not found.")
    except Exception as e:
        print(f"An error occurred: {str(e)}")

if __name__ == "__main__":
    image_name_to_remove = "cell_cell_0"
    remove_docker_image_by_name(image_name_to_remove)
