import subprocess
import sys


def install_package(package_name: str, upgrade: bool = False):
    # sys.executable 指向当前运行此 Python 脚本的解释器路径
    args = [sys.executable, "-m", "pip", "install"]

    if upgrade:
        args.append("--upgrade")

    args.append(package_name)

    try:
        # check=True 表示如果 pip 安装失败（返回码非 0），会自动抛出 CalledProcessError 异常
        # 不捕获 stdout/stderr，意味着 pip 的进度条会完美地直接显示在用户的终端上
        subprocess.run(args, check=True)

        print(f"✅ 成功安装 {package_name}!")

    except subprocess.CalledProcessError as e:
        # 这里处理安装失败的逻辑
        print(f"❌ 安装失败，退出码: {e.returncode}", file=sys.stderr)
    except Exception as e:
        # 处理其他系统级异常
        print(f"⚠️ 发生未知错误: {e}", file=sys.stderr)
