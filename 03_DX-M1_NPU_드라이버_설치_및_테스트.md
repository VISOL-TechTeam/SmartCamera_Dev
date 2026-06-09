# 03. DX-M1(NPU) 드라이버 설치 및 테스트

## 1. 목적

**DXRT·드라이버가 없는 깨끗한 OS**에 DeepX M1 NPU를 장착하고, [dx-all-suite](https://github.com/DEEPX-AI/dx-all-suite)를 **처음부터 클론·설치**한 뒤 첫 추론 데모까지 실행한다.

## 2. 시작 상태

| 항목 | 이 단계 시작 시 |
|---|---|
| DeepX M1 | M.2 슬롯에 **미장착** 또는 장착만 하고 드라이버 없음 |
| dx-all-suite | **없음** |
| `dxrt-cli` | **없음** |
| NPU 드라이버 | **미로드** |

01·02번(OS, SSH)이 완료되어 **SSH로 원격 작업**하는 것을 권장한다.

## 3. 사전 조건

- [01_OrangePi5Max_OS_설치.md](01_OrangePi5Max_OS_설치.md), [02_SSH_연결_및_설정.md](02_SSH_연결_및_설정.md) 완료
- Orange Pi **전원 OFF**
- DeepX M1 M.2 모듈, 나사·간격대(포함 시) 준비
- 인터넷 연결 (git clone, 설치 스크립트 다운로드)

## 4. DeepX M1 하드웨어 장착

1. Orange Pi **전원 OFF**, USB·HDMI 분리
2. M.2 슬롯에 DeepX M1을 규격에 맞게 삽입·고정
3. 전원·LAN·(필요 시) HDMI 연결 후 부팅

장착 후 PCIe 인식 확인:

```bash
lspci | grep -i deepx
dmesg | tail -50
```

아무것도 안 보이면 전원 OFF 후 재장착.

## 5. 구성 요소

| 항목 | 설명 |
|---|---|
| DeepX M1 | M.2 NPU |
| DXRT | 런타임·드라이버·`dxrt-cli` |
| dx-all-suite | DXRT, dx_app, dx_stream 통합 저장소 |
| dx_app | 샘플 추론 데모 |
| dx_stream | GStreamer 영상 파이프라인 (심화) |

공식 문서: [Setting Up Environment](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/02_Setting_Up_Environment.md)

## 6. 설치 전 패키지

SSH 접속 후:

```bash
sudo apt update
sudo apt install -y git build-essential pkg-config make \
  libgl1-mesa-glx libglib2.0-0
```

01번에서 `git`, `build-essential`을 이미 설치했다면 생략 가능.

## 7. dx-all-suite 클론

홈 디렉터리에서 **서브모듈 포함** 클론 (빈 폴더에서 시작):

```bash
cd ~
git clone --recurse-submodules https://github.com/DEEPX-AI/dx-all-suite.git
cd dx-all-suite
git submodule status
```

서브모듈 앞에 `-`가 있으면:

```bash
git submodule update --init --recursive
```

설치 경로: `~/dx-all-suite` (이후 문서 기준).

## 8. DX-Runtime 설치 (드라이버 + RT + App)

DEEPX 공식 로컬 설치:

```bash
cd ~/dx-all-suite
./dx-runtime/install.sh --all
```

- 펌웨어가 이미 최신이면: `./dx-runtime/install.sh --all --exclude-fw`
- 설치 중 오류 시: [FAQ Troubleshooting](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/05_FAQ_Troubleshooting_Guide.md)

설치 스크립트가 `venv-dx-runtime` 등을 자동 구성한다. **수동 venv 생성은 필요 없다.**

## 9. 재부팅 (필수)

NPU 커널 드라이버 로드를 위해 **반드시 재부팅**한다. DEEPX 문서는 cold boot(전원 OFF→ON)를 권장하기도 한다.

```bash
sudo reboot
```

재부팅 후 SSH로 다시 접속.

## 10. M1 장치 확인

```bash
dxrt-cli -s
```

성공 예 (버전은 설치본에 따라 다름):

```text
DX-RT v3.x.x
* Device 0: M1, Accelerator type
* RT Driver version : vX.X.X
* FW version :      vX.X.X
```

실패 시:

| 확인 | 명령 |
|---|---|
| M.2 장착 | 전원 OFF 후 재장착 |
| PCIe | `lspci`, `dmesg \| grep -i deepx` |
| 드라이버 | `./dx-runtime/install.sh --target=dx_rt_npu_linux_driver` 재실행 후 reboot |
| 무결성 | `~/dx-all-suite/dx-runtime/scripts/sanity_check.sh` |

## 11. 첫 추론 데모 (dx_app)

### 11.1 리소스 준비

```bash
cd ~/dx-all-suite/dx-runtime/dx_app
./setup.sh
```

모델·샘플 이미지를 다운로드한다. 네트워크·디스크 여유 필요.

### 11.2 대화형 데모

```bash
./run_demo.sh
```

터미널에 표시되는 번호를 입력해 C++ 데모 실행.

### 11.3 Python 데모 (선택)

```bash
./run_demo_python.sh
```

### 11.4 getting-started 파이프라인 (선택)

컴파일·런타임 전체 흐름: [Running Your First NPU Model](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/03_Running_Your_First_NPU_Model.md)

```bash
cd ~/dx-all-suite
./getting-started/runtime-0_install_dx-runtime.sh
./getting-started/runtime-1_setup_input_path.sh
./getting-started/runtime-2_setup_assets.sh
./getting-started/runtime-3_run_example_using_dxrt.sh
```

`.dxnn` 모델이 없으면 compiler 단계(Step 0~4)를 먼저 수행해야 한다.

## 12. dx_stream (심화, 선택)

카메라·영상 파이프라인은 04번 UVC 완료 후:

```bash
cd ~/dx-all-suite/dx-runtime/dx_stream
./setup.sh
./run_demo.sh
```

RTSP/WebRTC 연동: [RK3588_DeepX_M1_run_demo_9번_WebRTC_연동작업.md](../RK3588_DeepX_M1_run_demo_9번_WebRTC_연동작업.md)

## 13. 트러블슈팅

### 13.1 dxrt-cli -s 에 M1 없음

```bash
sudo reboot
# 또는 전원 OFF 10초 → ON
dxrt-cli -s
```

### 13.2 install.sh 실패

```bash
cd ~/dx-all-suite
./dx-runtime/scripts/sanity_check.sh
```

FAIL 항목의 모듈만 재설치:

```bash
./dx-runtime/install.sh --target=<module_name>
```

### 13.3 run_demo / setup.sh 오류

```bash
cd ~/dx-all-suite/dx-runtime/dx_app
./setup.sh
ldd ./bin/* 2>/dev/null | grep "not found"
```

## 14. 완료 확인

- [ ] M.2 DeepX M1 물리 장착
- [ ] `git clone --recurse-submodules` 완료
- [ ] `./dx-runtime/install.sh --all` 및 **reboot**
- [ ] `dxrt-cli -s`에서 Device 0: M1
- [ ] `dx_app/setup.sh` + `run_demo.sh` 실행

## 15. 다음 단계

→ [04_USB_UVC_카메라_테스트.md](04_USB_UVC_카메라_테스트.md): USB 카메라 연결 및 캡처 테스트

## 16. 참고

| 분류 | URL |
|---|---|
| dx-all-suite | https://github.com/DEEPX-AI/dx-all-suite |
| 설치 가이드 | https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/02_Setting_Up_Environment.md |
| DEEPX Developer Portal | https://developer.deepx.ai |

**기존 장비 이전**(`orangepi`→`camera`, 경로 캐시 등)은 [OrangePI_계정생성_파일권한복사_방법.md](../OrangePI_계정생성_파일권한복사_방법.md), [docs/PROJECT_BASELINE.md](../docs/PROJECT_BASELINE.md) 참조 — **신규 클린 설치에는 해당 없음**.
