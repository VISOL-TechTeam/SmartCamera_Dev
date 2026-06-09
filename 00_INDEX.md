# Orange Pi 5 Max 교육자료 통합 인덱스

## 1. 교육 목표

**공장 출하 직후 또는 OS가 없는 깨끗한 상태**에서 Orange Pi 5 Max를 세팅하고, **OS 설치 → SSH 원격 접속 → DX-M1(NPU) 드라이버 설치/테스트 → USB UVC 카메라 테스트**까지 처음부터 구성한다.

| 단계 | 문서 | 핵심 결과 |
|---|---|---|
| 1 | [01_OrangePi5Max_OS_설치.md](01_OrangePi5Max_OS_설치.md) | OS 이미지 굽기, 첫 부팅, 기본 패키지, CMA 적용 |
| 2 | [02_SSH_연결_및_설정.md](02_SSH_연결_및_설정.md) | IP 확인, PowerShell·VS Code Remote-SSH, SSH 서버·키·SCP |
| 3 | [03_DX-M1_NPU_드라이버_설치_및_테스트.md](03_DX-M1_NPU_드라이버_설치_및_테스트.md) | dx-all-suite 클론·설치, M1 인식, 첫 추론 데모 |
| 4 | [04_USB_UVC_카메라_테스트.md](04_USB_UVC_카메라_테스트.md) | 테스트 도구 설치, UVC 인식, ffmpeg 캡처 |

## 2. 시작 전 상태 (전제)

이 커리큘럼은 아래가 **없는** 상태에서 시작한다.

| 항목 | 시작 시 상태 |
|---|---|
| OS | microSD/eMMC에 **아무것도 기록되지 않음** (또는 공장 초기화) |
| Linux 계정 | **없음** (01번에서 OS 설치 후 이미지 기본 계정만 존재) |
| SSH | 서버 **미설치**, 키 **미등록** |
| DX-M1 / DXRT | 드라이버·런타임 **미설치**, `dx-all-suite` **없음** |
| 카메라 테스트 도구 | `v4l-utils`, `ffmpeg` **미설치** |
| CMA | 기본값(약 8MB) — **256M 미적용** |

저장소의 `ssh_keys/`, `/home/camera`, `/home/orangepi/dx-all-suite` 등은 **기존 작업 장비 흔적**이며, 이 교육 과정에서는 새로 만든다.

## 3. 교육 대상

- Orange Pi 5 Max / RK3588 보드를 **처음부터** 세팅하는 개발자
- DeepX M1 NPU와 USB 카메라를 **신규 환경**에 연동하려는 작업자

## 4. 예상 소요 시간

| 문서 | 예상 시간 | 비고 |
|---|---|---|
| 01 OS 설치 | 1~2시간 | 이미지 다운로드·굽기·첫 부팅 포함 |
| 02 SSH 설정 | 45~90분 | IP 확인 + SSH 서버·Windows 키 |
| 03 DX-M1 | 2~3시간 | dx-all-suite 클론·설치·재부팅·데모 포함 |
| 04 UVC 카메라 | 10~30분 | 패키지 설치·캡처·트러블슈팅 |
| **합계** | **약 4~6시간** | 네트워크·다운로드 속도에 따라 변동 |

## 5. 사전 준비물

### 하드웨어

| 항목 | 설명 |
|---|---|
| Orange Pi 5 Max | RK3588, DeepX M1 M.2 슬롯 (03번 전 M.2 장착) |
| DeepX M1 | M.2 NPU 모듈 — 03번 **시작 전** 장착 |
| USB UVC 카메라 | MJPEG 지원 권장 (04번) |
| microSD | 32GB 이상, **비어 있는** 카드 |
| USB SD 카드 리더 | Windows PC |
| HDMI 모니터 + USB 키보드 | Desktop 이미지 첫 설정 또는 Server 콘솔 |
| LAN 케이블 | 유선 네트워크 권장 |

### 소프트웨어 (Windows PC)

| 항목 | 용도 | 링크 |
|---|---|---|
| balenaEtcher | OS 이미지 굽기 | https://etcher.balena.io/ |
| OpenSSH Client | IP SSH 접속, 키 생성, scp | Windows 10/11 기본 포함 |
| VS Code + Remote-SSH | 원격 폴더·터미널 (**02번 11절**) | https://code.visualstudio.com/ |
| Git (선택) | Windows에서 저장소 clone 시 | https://git-scm.com/ |

## 5.1 공식 링크 및 소스

| 분류 | 항목 | URL |
|---|---|---|
| OS | Ubuntu Rockchip v2.4.0 | https://github.com/Joshua-Riek/ubuntu-rockchip/releases/tag/v2.4.0 |
| Tools | balenaEtcher | https://etcher.balena.io/ |
| Driver / Source | DEEPX dx-all-suite | https://github.com/DEEPX-AI/dx-all-suite |
| DX-AllSuite 설치 가이드 | Setting Up Environment | https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/02_Setting_Up_Environment.md |
| DX-AllSuite 첫 추론 | Running Your First NPU Model | https://github.com/DEEPX-AI/dx-all-suite/blob/main/docs/source/03_Running_Your_First_NPU_Model.md |

## 6. 완료 후 환경 기준

01~04를 모두 마치면 아래 상태가 된다.

| 항목 | 값 |
|---|---|
| OS | Ubuntu Rockchip (aarch64) |
| 작업 계정 | 이미지 기본 `ubuntu` 또는 01번에서 생성한 계정 |
| 홈 경로 | `/home/ubuntu` (또는 생성한 계정 홈) |
| dx-all-suite | `~/dx-all-suite` (클론·설치 완료) |
| DXRT | `dxrt-cli -s`로 M1 인식 |
| CMA | `cma=256M` 적용 |
| SSH | PowerShell·VS Code Remote-SSH `<USER>@<IP>` 키 접속 |

## 7. 학습 순서

```text
[빈 SD 카드 + 전원 OFF M.2 슬롯]
       |
[01 OS 설치]
  -> 이미지 굽기, 첫 부팅, apt, cma=256M, git 등 기본 도구
       |
[02 SSH]
  -> IP 확인, ssh USER@IP, openssh-server, Windows 키, VS Code Remote-SSH
       |
[03 DX-M1]  (전원 OFF → M.2 장착 → 전원 ON)
  -> dx-all-suite clone, install.sh, reboot, dxrt-cli, run_demo
       |
[04 UVC]  (USB 카메라 연결)
  -> v4l-utils/ffmpeg 설치, v4l2-ctl, ffmpeg 1프레임 캡처
```

각 단계는 **이전 단계를 처음부터 끝까지 완료한 뒤** 다음으로 진행한다.

## 8. 산출물 형식

| 형식 | 경로 | 용도 |
|---|---|---|
| Markdown (원본) | `교육자료/0X_*.md` | GitHub/Codex 작업 기준 |

## 9. 기존 작업 문서와의 관계

| 구분 | 이 교육자료 | 저장소 기존 문서 |
|---|---|---|
| 대상 | **신규 클린 설치** | 이미 구성된 장비 운영·복구·디버깅 |
| 계정 | `ubuntu` 등 새 계정 | `camera`, `orangepi` 이전 |
| DX-M1 | dx-all-suite **처음 설치** | dx_stream WebRTC, IR-CUT 등 **심화** |

심화 주제는 [docs/ORANGE_PI_WORKLOG_INDEX.md](../docs/ORANGE_PI_WORKLOG_INDEX.md)를 참조한다.
