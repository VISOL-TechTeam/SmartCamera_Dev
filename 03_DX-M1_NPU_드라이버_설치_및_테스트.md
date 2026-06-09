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

## 6. 설치 전 패키지 (DKMS·커널 헤더)

`install.sh`가 NPU **DKMS 드라이버**(`.deb`)를 빌드·설치할 때 **dkms**, **현재 커널용 linux-headers**, **build-essential**이 필요하다.  
**8절 `install.sh` 실행 전**에 아래를 **먼저** 설치하고 확인한다.

### 6.1 커널 버전 확인

```bash
uname -r
```

예: `6.1.0-1025-rockchip` — Orange Pi Rockchip 이미지는 **`-rockchip` 접미사**가 붙는다.

> **주의:** `6.8.0-124-generic` 등 **generic** 커널·headers는 Orange Pi Rockchip 보드와 **다른 계열**이다. `uname -r`에 `-rockchip`이 보이면 **generic headers는 설치하지 않는다.**

### 6.2 필수 패키지 설치

```bash
sudo apt update
sudo apt install -y dkms build-essential pkg-config make git \
  libgl1-mesa-glx libglib2.0-0 \
  linux-headers-$(uname -r)
```

`linux-headers-$(uname -r)` 설치가 실패하면(패키지 없음):

```bash
apt search linux-headers-$(uname -r | cut -d- -f1-2)
sudo apt install -y linux-headers-<위 검색 결과의 정확한 패키지명>
```

> 공식 안내의 `linux-headers-6.1.0-1025-rockchip`은 **예시**이다. 본인 `uname -r` 출력과 **일치하는** headers를 설치해야 한다.

01번에서 `git`, `build-essential`을 이미 설치했다면 중복 설치는 생략해도 된다. **dkms·linux-headers는 반드시 확인.**

### 6.3 설치 확인 (install.sh 전)

아래가 모두 통과해야 **8절**로 진행한다.

```bash
dpkg -l dkms | grep ^ii
dpkg -l "linux-headers-$(uname -r)" | grep ^ii
dpkg -l build-essential | grep ^ii
test -d "/usr/src/linux-headers-$(uname -r)" && echo "headers OK" || echo "headers MISSING"
```

| 확인 | 기대 |
|---|---|
| `dkms` | `ii` 상태 |
| `linux-headers-$(uname -r)` | `ii` 상태 |
| `/usr/src/linux-headers-$(uname -r)` | 디렉터리 존재 |

하나라도 `MISSING`이면 **6.2**를 다시 실행하거나 `apt search linux-headers`로 맞는 패키지를 찾은 뒤 설치한다.

### 6.4 Orange Pi — rockchip 전용 headers (사전 방지)

Orange Pi 5 Max + Ubuntu Rockchip에서는 아래만 사용한다.

| 설치함 | 설치하지 않음 |
|---|---|
| `linux-headers-$(uname -r)` (예: `linux-headers-6.1.0-1025-rockchip`) | `linux-headers-generic` |
| `linux-headers-rockchip` (메타, 선택) | `linux-headers-6.8.0-124-generic` 등 **generic** |

**왜 중요한가**

- `install.sh --all`이 `dxrt-driver-dkms` `.deb` 설치 시 **generic headers**(`6.8.0-124-*`)를 **의존성으로 같이 끌어올 수 있다.**
- 그러면 DKMS가 **부팅 커널(`6.1.0-1025-rockchip`)이 아니라 `6.8.0-124-generic`용**으로 빌드한다.
- 로그 예: `KERNEL_DIR=/lib/modules/6.8.0-124-generic/build` → **잘못된 커널**로 빌드 중.

**8절 전 확인**

```bash
uname -r
dpkg -l | grep linux-headers
sudo dkms status
```

| 항목 | 정상 (예) |
|---|---|
| `uname -r` | `6.1.0-1025-rockchip` |
| headers | `linux-headers-6.1.0-1025-rockchip` 만 `ii` |
| `dkms status` | `dxrt-driver-dkms ... 6.1.0-1025-rockchip ... installed` |
| **없어야 함** | `linux-headers-*-generic`, dpkg `iF` / `iU` |

### 6.5 generic headers 재설치 방지 (선택·권장)

과거 `install.sh`로 generic headers가 깔린 적이 있으면, **8절 전** hold로 재설치를 막는다.

```bash
sudo apt-mark hold linux-headers-6.8.0-124 linux-headers-6.8.0-124-generic linux-headers-generic
apt-mark showhold
```

Rockchip 커널·headers를 **업그레이드할 때**는 hold를 해제한다.

```bash
sudo apt-mark unhold linux-headers-6.8.0-124 linux-headers-6.8.0-124-generic linux-headers-generic
```

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

### 8.0 홈 디렉터리 권한 ( `_apt` Permission denied 대비)

7절 clone 후, `install.sh` 실행 **직전**에 확인한다. 홈 디렉터리가 `700`이면 `_apt`가 `~/dx-all-suite` 아래 `.deb`를 읽지 못한다.

```text
couldn't be accessed by user '_apt'. - pkgAcquire::Run (13: Permission denied)
E: Sub-process /usr/bin/dpkg returned an error code (1)
```

```bash
chmod o+x ~
chmod -R o+rX ~/dx-all-suite/dx-runtime/dx_rt_npu_linux_driver
```

### 8.1 install.sh 실행 방식

**첫 설치 (드라이버·runtime 모두 없음)**

```bash
cd ~/dx-all-suite
./dx-runtime/install.sh --all
```

- 펌웨어가 이미 최신이면: `./dx-runtime/install.sh --all --exclude-fw`
- **6.4·6.5** 사전 확인 후 실행. generic headers가 끼어 들어가면 **8.2** 또는 **13.2**로 정리.

**드라이버가 이미 rockchip 커널에 installed인 경우**

`sudo dkms status`에 `dxrt-driver-dkms ... $(uname -r) ... installed`가 있고 `lsmod | grep dxrt`가 보이면 **`--all`을 다시 쓰지 않는다** (generic headers 재설치·dpkg 오류 유발).

runtime·앱만 설치:

```bash
./dx-runtime/install.sh --help    # 사용 가능한 --target 확인
./dx-runtime/install.sh --target=dx_rt
./dx-runtime/install.sh --target=dx_app
```

설치 중 오류 시: [FAQ Troubleshooting](https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/05_FAQ_Troubleshooting_Guide.md) · **13절**

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
lsmod | grep -E 'dxrt|dx_dma'
```

| 결과 | 의미 |
|---|---|
| `dxrt-cli -s`에 M1 표시 | 드라이버 + runtime 정상 |
| `dxrt-cli: command not found` 이지만 `dxrt_driver` 모듈 로드됨 | **커널 드라이버만** 설치됨 → **8.1** runtime target 설치 |
| 둘 다 없음 | **13.1** · M.2 장착·드라이버 재설치 |

`dxrt-cli`가 PATH에 없을 때:

```bash
find ~/dx-all-suite/dx-runtime -name dxrt-cli 2>/dev/null
source ~/dx-all-suite/dx-runtime/venv-dx-runtime/bin/activate
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

카메라·영상 파이프라인은 **03번 8절(dx-runtime)·10절(M1 확인)** 및 **04번 UVC** 완료 후 진행한다.

```bash
cd ~/dx-all-suite/dx-runtime/dx_stream
./install.sh
./setup.sh
./run_demo.sh
```

| 순서 | 스크립트 | 설명 |
|---|---|---|
| 1 | `./install.sh` | dx_stream **의존성 설치·로컬 환경 구성** (`run_demo.sh` **전 필수**) |
| 2 | `./setup.sh` | NPU 모델·샘플 영상 등 에셋 다운로드 |
| 3 | `./run_demo.sh` | 대화형 AI 데모 선택·실행 |

`./install.sh` 없이 `./run_demo.sh`만 실행하면 의존성·빌드 미완료로 실패할 수 있다.

03번 **8.1**에서 `./dx-runtime/install.sh --all`(또는 `--target=dx_stream`)을 이미 실행했다면, `dx_stream` 디렉터리 `./install.sh`는 **run_demo 직전**에 한 번 더 실행해 로컬 패키지·venv를 맞춘다.

설치·빌드 오류 시:

```bash
cd ~/dx-all-suite/dx-runtime/dx_stream
./install.sh
./setup.sh
```


## 13. 트러블슈팅

### 13.1 dxrt-cli -s 에 M1 없음

```bash
sudo reboot
# 또는 전원 OFF 10초 → ON
dxrt-cli -s
```

### 13.2 DKMS / linux-headers / dpkg 오류 (종합)

#### 증상 A — install.sh·dpkg 실패

```text
Failed to install dkms package. Exiting...
couldn't be accessed by user '_apt'. Permission denied
E: Sub-process /usr/bin/dpkg returned an error code (1)
linux-headers-6.8.0-124-generic
iF / iU (dpkg 상태)
```

**원인**

| 원인 | 설명 |
|---|---|
| `_apt` Permission denied | 홈(`700`) 아래 `.deb`를 apt가 읽지 못함 |
| generic headers | `linux-headers-*-generic` 설치·설정 실패 |
| bcmdhd-sdio autoinstall | Wi-Fi DKMS가 headers postinst에서 실패해 연쇄 오류 (rockchip에서는 보통 `installed`) |

**조치 1 — 홈 권한**

```bash
chmod o+x ~
chmod -R o+rX ~/dx-all-suite/dx-runtime/dx_rt_npu_linux_driver
```

**조치 2 — 잘못된 커널(6.8 generic)용 dxrt DKMS 제거**

```bash
uname -r
sudo dkms remove dxrt-driver-dkms/2.4.1-2 -k 6.8.0-124-generic
sudo dkms status
```

버전·커널 문자열은 `dkms status` 출력에 맞게 바꾼다. **rockchip 쪽 `installed`는 유지.**

**조치 3 — generic headers 제거**

```bash
sudo apt-mark unhold linux-headers-6.8.0-124 linux-headers-6.8.0-124-generic linux-headers-generic 2>/dev/null

sudo dpkg --purge --force-depends \
  linux-headers-6.8.0-124-generic \
  linux-headers-generic \
  linux-headers-6.8.0-124

sudo apt --fix-broken install -y
sudo dpkg --configure -a
dpkg -l | grep linux-headers
```

남아야 할 것: `linux-headers-$(uname -r)` (`ii`), `linux-headers-rockchip` (`ii`). **`iF` / `iU` / `6.8` generic 없음.**

**조치 4 — 재설치 방지 후 runtime만**

```bash
sudo apt-mark hold linux-headers-6.8.0-124 linux-headers-6.8.0-124-generic linux-headers-generic

cd ~/dx-all-suite
./dx-runtime/install.sh --target=dx_rt
```

드라이버가 rockchip에 없을 때만:

```bash
./dx-runtime/install.sh --target=dx_rt_npu_linux_driver
```

#### 증상 B — DKMS가 6.8 generic으로 빌드

```text
KERNEL_DIR=/lib/modules/6.8.0-124-generic/build
Building module: ... make ... KERNEL_DIR=...
```

**원인:** generic headers 패키지가 설치·설정되면서 `header_postinst.d/dkms`가 **6.8** 기준 autobuild 실행.

**조치:** **13.2 조치 2~4** 실행. `uname -r`은 `6.1.0-1025-rockchip`인데 빌드가 6.8이면 **headers 패키지가 잘못 깔린 것**.

rockchip만 다시 빌드·설치:

```bash
sudo dkms build dxrt-driver-dkms/2.4.1-2 -k $(uname -r)
sudo dkms install dxrt-driver-dkms/2.4.1-2 -k $(uname -r)
sudo dkms status
```

#### 증상 C — 의존성·headers 누락 (공식 install.sh 메시지)

```text
Required packages: dkms, linux-headers for your kernel, build-essential
sudo apt-get install -y dkms linux-headers-6.1.0-1025-rockchip build-essential
```

**조치:** 예시 버전 그대로 쓰지 말고 **6.2·6.3** (`linux-headers-$(uname -r)`) 실행 후 **8.1** 재시도.

#### 증상 D — dxrt-cli 없음, 모듈은 로드됨

```bash
lsmod | grep dxrt    # dxrt_driver, dx_dma 있음
dxrt-cli -s          # command not found
```

**조치:** 드라이버는 정상. **8.1** `--target=dx_rt` 등으로 runtime 설치. **13.2 조치 3~4**로 dpkg 정리 후 진행.

#### 무결성 점검

```bash
cd ~/dx-all-suite
./dx-runtime/scripts/sanity_check.sh
```

FAIL 항목만:

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
- [ ] `uname -r`이 `-rockchip` 커널, **generic headers 없음** (6.4)
- [ ] `dkms`, `linux-headers-$(uname -r)`, `build-essential` 설치·확인 (6.2~6.3)
- [ ] `git clone --recurse-submodules` 완료
- [ ] `./dx-runtime/install.sh` 완료 및 **reboot**
- [ ] `sudo dkms status` — `dxrt-driver-dkms`가 **현재 커널**에 `installed`
- [ ] `dxrt-cli -s`에서 Device 0: M1
- [ ] `dx_app/setup.sh` + `run_demo.sh` 실행
- [ ] (선택) `dx_stream`: `./install.sh` → `./setup.sh` → `./run_demo.sh`

## 15. 다음 단계

→ [04_USB_UVC_카메라_테스트.md](04_USB_UVC_카메라_테스트.md): USB 카메라 연결 및 캡처 테스트

## 16. 참고

| 분류 | URL |
|---|---|
| dx-all-suite | https://github.com/DEEPX-AI/dx-all-suite |
| 설치 가이드 | https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/02_Setting_Up_Environment.md |
| DEEPX Developer Portal | https://developer.deepx.ai |


