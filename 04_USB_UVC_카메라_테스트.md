# 04. USB UVC 카메라 테스트

## 문서 안내

| 항목 | 내용 |
|---|---|
| **커리큘럼** | **4 / 4** — USB UVC 카메라 |
| **선행** | [01](01_OrangePi5Max_OS_설치.md) **CMA 256M**, [02](02_SSH_연결_및_설정.md) (원격 시) |
| **작업 위치** | Orange Pi (SSH 또는 HDMI) |
| **완료 기준** | `/dev/video*` 인식, **`test.jpg`** 1장 캡처 |
| **다음** | [05_SmartCamera_App_설치_및_실행.md](05_SmartCamera_App_설치_및_실행.md) |

| 이 문서에서 함 | 이 문서에서 하지 않음 |
|---|---|
| v4l2·ffmpeg **단독** 카메라 검증, CMA 재확인 | NPU 설치, SmartCamera App (→ **05**) |

### 작업 흐름

```text
[§4~5] 도구 설치·CMA 확인
    → [§6] USB 연결·lsusb
    → [§7] v4l2-ctl 포맷 확인
    → [§8] ffmpeg 1프레임 → test.jpg
```

> **원칙:** 앱(nori, dx_stream 실카메라) 실행 **전에** 이 문서로 카메라만 먼저 검증한다.

---

## 1. 목적

**카메라 테스트 도구가 없는 깨끗한 OS**에 USB UVC 카메라를 연결하고, 패키지 설치부터 장치 인식·단일 프레임 캡처까지 **처음부터** 검증한다.

## 2. 시작 상태

| 항목 | 이 단계 시작 시 |
|---|---|
| USB UVC 카메라 | **미연결** |
| `v4l-utils`, `ffmpeg` | **미설치** (01번에서 일괄 설치하지 않았다면) |
| `/dev/video*` | 카메라 없으면 **없음** |
| CMA | 01번에서 `cma=256M` **적용 완료** 전제 |

애플리케이션(`nori_camera_server`, `dx_stream` 실카메라 등)은 **아직 실행하지 않은** 상태에서 카메라만 검증한다.

## 3. 사전 조건

- [01_OrangePi5Max_OS_설치.md](01_OrangePi5Max_OS_설치.md) — 특히 **CMA 256M**
- [02_SSH_연결_및_설정.md](02_SSH_연결_및_설정.md) — 원격 테스트 시
- USB UVC 카메라 (MJPEG 640x480 지원 권장)

---

## A. 준비

## 4. 테스트 도구 설치

01번에서 설치하지 않았다면:

```bash
sudo apt update
sudo apt install -y v4l-utils ffmpeg
```

GStreamer 영상 파이프라인(선택):

```bash
sudo apt install -y gstreamer1.0-tools gstreamer1.0-plugins-base \
  gstreamer1.0-plugins-good gstreamer1.0-plugins-bad gstreamer1.0-rtsp
```

확인:

```bash
v4l2-ctl --version
ffmpeg -version | head -1
```

## 5. CMA 확인

01번을 건너뛰었거나 미적용이면 **카메라 테스트 전** 반드시 적용한다.

```bash
cat /proc/meminfo | grep -i Cma
cat /proc/cmdline
```

| CmaTotal | 조치 |
|---|---|
| ~8192 kB | [01번 8절](01_OrangePi5Max_OS_설치.md) `cma=256M` 적용 후 reboot |
| ~262144 kB | 다음 단계 |

---

## B. 장치 인식 · 캡처

## 6. USB 카메라 연결

1. Orange Pi **부팅된 상태**에서 USB 포트에 UVC 카메라 연결
2. 전원 허브 사용 시 **powered hub** 권장

```bash
lsusb
dmesg | tail -30
```

`uvcvideo` 또는 카메라 제조사 이름이 보이면 커널 인식 성공.

## 7. V4L2 장치 확인

```bash
ls -l /dev/video*
v4l2-ctl --list-devices
```

예:

```text
USB Camera: USB Camera
        /dev/video0
        /dev/video1
```

캡처는 보통 `/dev/video0`. 포맷 확인:

```bash
v4l2-ctl -d /dev/video0 --list-formats-ext
```

**MJPEG 640x480** 이 있으면 1차 테스트에 적합.

## 8. 단일 프레임 캡처

**다른 앱 없이** ffmpeg만 사용:

```bash
cd ~
ffmpeg -f v4l2 -input_format mjpeg -video_size 640x480 -framerate 15 \
  -i /dev/video0 -frames:v 1 test.jpg
ls -la test.jpg
```

성공: `test.jpg` 파일 생성.

Windows로 복사 (02번에서 만든 키):

```powershell
scp -i "$env:USERPROFILE\.ssh\id_ed25519_orangepi" <USER>@<ORANGE_PI_IP>:~/test.jpg .
```

### YUYV 포맷만 있는 경우

```bash
ffmpeg -f v4l2 -video_size 640x480 -framerate 15 \
  -i /dev/video0 -frames:v 1 test_yuyv.jpg
```

---

## C. 보조 확인 (선택)

## 9. 점유 프로세스 확인

캡처 실패·hang 시:

```bash
sudo fuser -v /dev/video*
```

Desktop 환경에서 PipeWire가 점유할 수 있다:

```bash
systemctl --user stop pipewire wireplumber pipewire-pulse 2>/dev/null
sudo fuser -v /dev/video*
```

## 10. GStreamer 확인 (선택)

03·04 이후 영상 파이프라인용:

```bash
gst-inspect-1.0 | grep -Ei "v4l2src|mpph264enc|rtspclientsink"
```

| 플러그인 | 용도 |
|---|---|
| `v4l2src` | V4L2 카메라 입력 |
| `mpph264enc` | RK3588 H.264 HW 인코더 |
| `rtspclientsink` | RTSP publish |

## 11. 권장 테스트 순서 (요약)

1. CMA 256M 확인 (§5)
2. `apt install v4l-utils ffmpeg` (§4)
3. USB 연결 → `lsusb` (§6)
4. `v4l2-ctl --list-devices` (§7)
5. `ffmpeg ... test.jpg` (§8)

## 12. 트러블슈팅

| 증상 | 조치 |
|---|---|
| `/dev/video0` 없음 | USB 재연결, `dmesg`, 다른 포트·케이블 |
| ffmpeg hang | `fuser`, PipeWire 중지, MJPEG·해상도 낮추기 |
| UVC control -32 | powered hub, 640x480@15fps |
| CMA alloc failed | 01번 CMA 256M, reboot |
| HDMI 초록 화면 | CMA 확인 후 **앱 실행 전** ffmpeg 단독 테스트 |

로그:

```bash
dmesg | grep -iE "uvc|usb|video" | tail -50
journalctl -b -p warning..alert --no-pager | tail -50
```

## 13. 완료 확인

- [ ] `v4l-utils`, `ffmpeg` 설치
- [ ] USB 연결 후 `v4l2-ctl --list-devices`에 카메라 표시
- [ ] `ffmpeg`로 `test.jpg` 1장 생성
- [ ] (선택) Windows `scp`로 이미지 수신

---

## 14. 다음 단계

카메라 단독 테스트 통과 후:

| 주제 | 문서 |
|---|---|
| SmartCamera App (설치·실행) | [05_SmartCamera_App_설치_및_실행.md](05_SmartCamera_App_설치_및_실행.md) |
| dx_stream (샘플 영상) | [03 §12](03_DX-M1_NPU_드라이버_설치_및_테스트.md) |
| 전체 파이프라인 | [RK3588_DeepX_M1_스마트카메라_데이터파이프라인.md](../RK3588_DeepX_M1_스마트카메라_데이터파이프라인.md) |

## 15. 교육 커리큘럼 (04 완료)

→ [05_SmartCamera_App_설치_및_실행.md](05_SmartCamera_App_설치_및_실행.md) 계속.
