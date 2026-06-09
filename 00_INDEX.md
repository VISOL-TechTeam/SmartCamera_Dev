# Orange Pi 5 Max 교육자료 통합 인덱스

클린 설치 기준 **5단계** 교육 자료입니다. **00(본 문서) → 01 → 02 → 03 → 04 → 05** 순서로만 진행합니다.

---

## 1. 5단계 로드맵

| 단계 | 문서 | 한 줄 요약 | 작업 위치 | 완료 기준 |
|:---:|---|---|---|---|
| **0** | **00_INDEX** (본 문서) | 전체 흐름·준비물·범위 | — | 아래 로드맵 이해 |
| **1** | [01_OrangePi5Max_OS_설치.md](01_OrangePi5Max_OS_설치.md) | SD에 OS 굽기·부팅·CMA | **Windows PC** + Orange Pi(HDMI) | OS 부팅, `cma=256M` |
| **2** | [02_SSH_연결_및_설정.md](02_SSH_연결_및_설정.md) | Windows SSH 준비 → Pi 원격 접속 | **Windows PC** + Orange Pi | 키로 `ssh`·VS Code 접속 |
| **3** | [03_DX-M1_NPU_드라이버_설치_및_테스트.md](03_DX-M1_NPU_드라이버_설치_및_테스트.md) | M1 장착·dx-all-suite·NPU 데모 | Orange Pi (SSH 권장) | `dxrt-cli -s` M1 인식 |
| **4** | [04_USB_UVC_카메라_테스트.md](04_USB_UVC_카메라_테스트.md) | USB 카메라 인식·1장 캡처 | Orange Pi (SSH 권장) | `test.jpg` 생성 |
| **5** | [05_SmartCamera_App_설치_및_실행.md](05_SmartCamera_App_설치_및_실행.md) | SmartCamera App 설치·웹 UI | Orange Pi (SSH 권장) | `:8001` 접속·API OK |

```text
[00] 준비·로드맵 파악
  |
[01] OS ────────────── Windows Etcher / Pi HDMI
  |
[02] SSH ───────────── Windows 먼저(OpenSSH·키) → Pi IP·ssh
  |
[03] DX-M1 ─────────── 전원 OFF M.2 장착 → dx-all-suite
  |
[04] UVC 카메라 ────── USB 연결 → ffmpeg 캡처
  |
[05] SmartCamera App ─ clone → Install.sh → start.sh → :8001
  |
[완료] 00_INDEX §10 최종 점검
```

---

## 2. 문서별 범위 (겹치지 않게)

| 문서 | **이 문서에서만** 다룸 | **다른 문서로 미룸** |
|---|---|---|
| **01** | 이미지 다운로드·Etcher·첫 부팅·Desktop 마법사·apt·CMA·diskpart | SSH, NPU, 카메라 앱 |
| **02** | OpenSSH·키 생성·IP 확인·ssh 서버·authorized_keys·VS Code·SCP | OS 굽기, dx-all-suite |
| **03** | M.2 장착·DKMS·headers·dx-all-suite·dxrt-cli·dx_app·(선택) dx_stream | UVC ffmpeg 상세, WebRTC |
| **04** | UVC 인식·v4l2·ffmpeg 1프레임·CMA 재확인 | NPU 설치, SmartCamera App |
| **05** | SmartCamera_App clone·Install.sh·start.sh·웹 UI | OS·SSH·dx-all-suite·UVC 상세 |

저장소의 `ssh_keys/`, `/home/camera`, 기존 `dx-all-suite` 경로는 **다른 장비 흔적**입니다. 이 교육에서는 **새로** 만듭니다.

---

## 3. 시작 전 상태 (전제)

| 항목 | 시작 시 |
|---|---|
| OS | microSD/eMMC **비어 있음** |
| Linux 계정 | **없음** (01 이후 이미지 기본 계정만) |
| SSH | 서버 **미설치**, Windows 키 **없음** |
| DX-M1 / DXRT | **미설치**, `dx-all-suite` **없음** |
| 카메라 도구 | `v4l-utils`, `ffmpeg` **미설치** |
| CMA | 기본 ~8MB (**256M 미적용**) |

---

## 4. 교육 목표

**공장 출하·OS 없는 상태**에서 Orange Pi 5 Max를 세팅하고, **OS → SSH → DX-M1(NPU) → USB UVC 카메라 → SmartCamera App**까지 처음부터 구성한다.

**대상:** Orange Pi 5 Max / RK3588을 처음 세팅하는 개발자, DeepX M1·UVC를 **신규 환경**에 붙이는 작업자.

---

## 5. 예상 소요 시간

| 문서 | 시간 | 비고 |
|---|---|---|
| 01 OS | 1~2시간 | 다운로드·굽기 포함 |
| 02 SSH | 45~90분 | Windows 키 선행 |
| 03 DX-M1 | 2~3시간 | clone·install·reboot |
| 04 UVC | 10~30분 | 캡처·트러블슈팅 |
| 05 SmartCamera App | 30~60분 | clone·Install·start·웹 확인 |
| **합계** | **약 5~7시간** | 네트워크 속도에 따라 변동 |

---

## 6. 사전 준비물

### 6.1 하드웨어 (단계별)

| 항목 | 필요 시점 | 설명 |
|---|---|---|
| Orange Pi 5 Max | 01~ | RK3588, 5V/4A 전원 |
| emmc/microSD 32GB+ | 01 | **빈** 카드, USB 리더 |
| HDMI·키보드·(마우스) | 01 | Desktop 마법사 / Server 콘솔 |
| LAN 케이블/Wifi ant | 01~ | DHCP 권장 |
| DeepX M1 M.2 | **03 시작 전** 장착 | 전원 OFF 후 삽입 |
| USB UVC 카메라 | 04 | MJPEG 권장 |

### 6.2 Windows PC 소프트웨어

| 항목 | 시점 | 링크 |
|---|---|---|
| balenaEtcher | 01 | https://etcher.balena.io/ |
| OpenSSH Client | 02 | Windows 10/11 기본 |
| VS Code + Remote-SSH | 02 (선택) | https://code.visualstudio.com/ |

---

## 7. 단계별 핵심 작업 (요약)

### 01 — OS 설치

1. Ubuntu Rockchip 이미지 다운로드 → Etcher 굽기  
2. 첫 부팅 (Desktop: 마법사 5단계)  
3. `apt upgrade`, 기본 패키지, **`cma=256M`**, reboot  

→ 상세: [01](01_OrangePi5Max_OS_설치.md)

### 02 — SSH

1. **Windows:** OpenSSH Client → `ssh-keygen`  
2. **Pi:** IP 확인 (`hostname -I`) → `openssh-server`  
3. **Windows:** 공개키 등록 → 키 접속 → (선택) VS Code  

→ 상세: [02](02_SSH_연결_및_설정.md)

### 03 — DX-M1

1. **전원 OFF** → M.2 장착  
2. `dkms` + `linux-headers-$(uname -r)` (**rockchip**, generic 금지)  
3. `git clone --recurse-submodules` → `./dx-runtime/install.sh` → **reboot**  
4. `dxrt-cli -s`, `dx_app/run_demo.sh`  

→ 상세: [03](03_DX-M1_NPU_드라이버_설치_및_테스트.md)

### 04 — UVC 카메라

1. CMA 256M 재확인  
2. USB 연결 → `v4l2-ctl`  
3. `ffmpeg` 1프레임 → `test.jpg`  

→ 상세: [04](04_USB_UVC_카메라_테스트.md)

### 05 — SmartCamera App

1. `git clone` SmartCamera_App  
2. `sudo ./Install.sh` (최초 1회)  
3. `./start.sh` → 브라우저 `http://<IP>:8001`  

→ 상세: [05](05_SmartCamera_App_설치_및_실행.md)

---

## 8. 완료 후 환경

| 항목 | 값 |
|---|---|
| OS | Ubuntu Rockchip (aarch64) |
| 계정 | `ubuntu` 또는 01 마법사 계정 |
| CMA | `cma=256M` |
| SSH | `ssh -i ... <USER>@<IP>` |
| NPU | `dxrt-cli -s` → Device 0: M1 |
| 카메라 | `/dev/video0`, `test.jpg` |
| SmartCamera App | `http://<IP>:8001`, `./start.sh --stop` 종료 |

---

## 9. 심화·기존 문서

| 구분 | 이 교육 (00~05) | 저장소 심화 문서 |
|---|---|---|
| 대상 | **클린 설치** | 운영·복구·WebRTC·IR-CUT |
| dx_stream 실카메라 | 03 §12 (샘플 영상) | [RK3588 파이프라인](../RK3588_DeepX_M1_스마트카메라_데이터파이프라인.md) |
| 인덱스 | 본 문서 | [docs/ORANGE_PI_WORKLOG_INDEX.md](../docs/ORANGE_PI_WORKLOG_INDEX.md) |

---

## 10. 최종 점검 체크리스트

01~05를 마친 뒤 전부 확인한다.

**01 OS**

- [ ] OS 부팅·(Desktop) 마법사 완료  
- [ ] `cma=256M` 적용 (`/proc/cmdline`, `CmaTotal`)

**02 SSH**

- [ ] Windows `ssh -V`, ed25519 키 생성  
- [ ] Pi `openssh-server`, 키 접속 성공  

**03 DX-M1**

- [ ] M.2 장착, `dxrt-driver-dkms` rockchip 커널 `installed`  
- [ ] `dxrt-cli -s` M1, `dx_app/run_demo.sh`  

**04 UVC**

- [ ] `v4l2-ctl --list-devices` 카메라 표시  
- [ ] `ffmpeg`로 `test.jpg` 1장  

**05 SmartCamera App**

- [ ] `~/SmartCamera_App`, `sudo ./Install.sh` 완료  
- [ ] `./start.sh` → `:8001` LISTEN, 브라우저 접속  
- [ ] `./start.sh --stop` 정상 종료  

---

## 11. 산출물

| 형식 | 경로 |
|---|---|
| Markdown | `교육자료/00_INDEX.md`, `01_*.md` … `05_*.md` |
