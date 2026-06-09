# -*- coding: utf-8 -*-
"""교육자료(클린 설치 기준) Markdown 핵심 내용을 DOCX 4종으로 생성."""

import os
from docx_utils import DocBuilder

OUT_DIR = os.path.join(os.path.dirname(__file__), 'docx')


def build_os_doc():
    b = DocBuilder()
    b.title('01. Orange Pi 5 Max OS 설치', '빈 SD · Ubuntu Rockchip · CMA 256M')
    b.para('비어 있는 microSD에 OS를 처음부터 설치한다.')
    b.h1('1. OS / Etcher')
    b.para('https://github.com/Joshua-Riek/ubuntu-rockchip/releases/tag/v2.4.0')
    b.para('https://etcher.balena.io/')
    b.h1('2. IP 확인 (02번용)')
    b.code('hostname -I')
    b.bullet('Server: ubuntu/ubuntu, SSH 포함 가능')
    b.bullet('Desktop: HDMI 1회, SSH 설치 필요할 수 있음')
    b.h1('3. CMA')
    b.code('cma=256M in boot config, sudo reboot')
    return b


def build_ssh_doc():
    b = DocBuilder()
    b.title('02. SSH 연결 및 설정', 'PowerShell · IP 접속 · SSH 서버 · 키')
    b.para('IP 확인 → ssh USER@IP → openssh-server → Windows 키·scp')

    b.h1('1. IP 확인')
    b.bullet('HDMI: hostname -I')
    b.bullet('공유기 DHCP')

    b.h1('2. IP 로그인 (PowerShell)')
    b.code('ssh ubuntu@192.168.0.42')

    b.h1('3. SSH 서버')
    b.code('sudo apt install -y openssh-server')
    b.code('sudo systemctl enable --now ssh')

    b.h1('4. 키 · SCP')
    b.bullet('-C: 키 주석(메모). 접속 IP와 무관')
    b.code('ssh-keygen -t ed25519 -f "%USERPROFILE%\\.ssh\\id_ed25519_orangepi" -C "ubuntu@192.168.0.42"')
    b.h1('5. VS Code Remote-SSH')
    b.bullet('확장: Remote - SSH')
    b.bullet('F1 → Connect to Host → orangepi5max')
    b.bullet('Open Folder: /home/ubuntu')
    return b


def build_dxm1_doc():
    b = DocBuilder()
    b.title('03. DX-M1(NPU) 드라이버 설치 및 테스트', 'dx-all-suite 클린 설치')
    b.para('SSH 원격 접속 상태에서 진행.')
    b.code('git clone --recurse-submodules https://github.com/DEEPX-AI/dx-all-suite.git')
    b.code('./dx-runtime/install.sh --all && sudo reboot')
    b.code('dxrt-cli -s')
    b.code('cd ~/dx-all-suite/dx-runtime/dx_app && ./setup.sh && ./run_demo.sh')
    return b


def build_uvc_doc():
    b = DocBuilder()
    b.title('04. USB UVC 카메라 테스트', '패키지 설치 · ffmpeg 1프레임')
    b.code('sudo apt install -y v4l-utils ffmpeg')
    b.code('ffmpeg -f v4l2 ... -i /dev/video0 -frames:v 1 test.jpg')
    return b


BUILDERS = [
    ('01_OrangePi5Max_OS_설치.docx', build_os_doc),
    ('02_SSH_연결_및_설정.docx', build_ssh_doc),
    ('03_DX-M1_NPU_드라이버_설치_및_테스트.docx', build_dxm1_doc),
    ('04_USB_UVC_카메라_테스트.docx', build_uvc_doc),
]


def main():
    os.makedirs(OUT_DIR, exist_ok=True)
    for filename, builder_fn in BUILDERS:
        path = os.path.join(OUT_DIR, filename)
        builder_fn().save(path)
        print(f'Created: {path}')


if __name__ == '__main__':
    main()
