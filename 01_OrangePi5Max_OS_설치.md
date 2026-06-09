# 01. Orange Pi 5 Max OS 설치

## 1. 목적

**비어 있는 microSD**에 Ubuntu Rockchip OS를 처음부터 설치하고, 첫 부팅·기본 패키지·영상 처리용 CMA까지 적용한다.

## 2. 시작 상태

| 항목 | 이 단계 시작 시 |
|---|---|
| microSD | **포맷되지 않았거나 비어 있음** |
| Orange Pi | OS 없음, 전원 OFF |
| 네트워크/SSH/DX-M1 | **아직 해당 없음** |

## 3. 준비물

| 항목 | 설명 |
|---|---|
| Orange Pi 5 Max | 5V/4A 이상 전원 |
| microSD | 32GB 이상, **데이터 백업 후 사용** (굽기 시 전체 삭제됨) |
| USB SD 카드 리더 | Windows PC |
| HDMI + USB 키보드 | Desktop: 설정 마법사 / Server: 콘솔 로그인 |
| LAN 케이블 | DHCP로 IP 받기 |

## 4. OS 이미지 다운로드

Orange Pi 5 Max / RK3588용 이미지:

| 항목 | 내용 |
|---|---|
| **릴리스** | [Ubuntu Rockchip v2.4.0](https://github.com/Joshua-Riek/ubuntu-rockchip/releases/tag/v2.4.0) |
| 저장소 | https://joshua-riek.github.io/ubuntu-rockchip-download/ |
| 보드 | 릴리스 페이지에서 **Orange Pi 5 Max** 항목 선택 |
| 형식 | `.img.xz` (압축) 또는 `.img` |

Desktop / Server 중 하나를 선택한다. Server는 SSH·headless에 적합하고, Desktop은 HDMI 마법사로 초기 설정한다.

## 5. 이미지 굽기 (Windows PC)

### 5.1 balenaEtcher

1. [balenaEtcher](https://etcher.balena.io/) 설치
2. **Flash from file** → 다운로드한 `.img.xz` 또는 `.img`
3. **Select target** → microSD (용량·장치명 확인 — PC 디스크 선택 금지)
4. **Flash!** → 완료 후 SD 분리

### 5.2 주의

- 굽기는 SD **전체를 덮어쓴다**. 기존 데이터는 복구 불가.
- 불량·저속 SD는 부팅 실패 원인이 될 수 있다.

## 6. 첫 부팅

1. microSD 삽입
2. HDMI, 키보드, **LAN** 연결
3. 전원 ON → 1~3분 대기

### 6.1 Ubuntu Server

| 항목 | 초기값 |
|---|---|
| 사용자 | `ubuntu` |
| 비밀번호 | `ubuntu` (첫 로그인 후 변경 권장) |

HDMI·시리얼 또는 이후 SSH(02번)로 로그인한다.

### 6.2 Ubuntu Desktop

HDMI에서 **설정 마법사**를 따라 사용자·비밀번호·Wi-Fi 등을 **새로 생성**한다. 마법사가 끝난 뒤 터미널을 연다.

## 7. 최초 시스템 설정

로그인 후 터미널에서 **순서대로** 실행한다.

### 7.1 패키지 업데이트

```bash
sudo apt update
sudo apt upgrade -y
```

### 7.2 시간대

```bash
sudo timedatectl set-timezone Asia/Seoul
timedatectl
```

### 7.3 기본 도구 (이후 단계용)

```bash
sudo apt install -y git curl wget build-essential pkg-config \
  v4l-utils ffmpeg \
  gstreamer1.0-tools gstreamer1.0-plugins-base gstreamer1.0-plugins-good \
  gstreamer1.0-plugins-bad gstreamer1.0-rtsp
```

03·04번에서 다시 설치해도 되지만, 한 번에 받아 두면 네트워크 설정이 단순해진다.

### 7.4 호스트 이름 (선택)

```bash
sudo hostnamectl set-hostname orangepi5max
hostname
```

mDNS(`*.local`)는 02번 SSH 문서에서 설정한다.

### 7.5 IP 확인 (02번 SSH 접속용)

Orange Pi가 LAN에서 IP를 받았는지 확인한다. 이 주소로 Windows PowerShell에서 `ssh <USER>@<IP>` 접속한다.

```bash
hostname -I
ip -4 addr show
```

| 항목 | 예시 |
|---|---|
| `<ORANGE_PI_IP>` | `192.168.0.42` |
| `<USER>` | Server: `ubuntu` / Desktop: 마법사에서 생성한 이름 |

**메모해 둔다.** HDMI 없이 작업하려면 02번에서 이 IP로 접속한다.

IP를 모를 때는 02번 4절(공유기 DHCP)을 참조한다.

### 7.6 Ubuntu Server vs Desktop

| 이미지 | SSH | 권장 |
|---|---|---|
| **Server** | `openssh-server` **포함** 가능 | HDMI 없이 PowerShell IP 접속 바로 시도 |
| **Desktop** | SSH **미포함** 가능 | HDMI 1회 → SSH 설치 → IP 접속 |

## 8. CMA 부팅 파라미터 (cma=256M)

카메라·HDMI·DMA는 **연속 물리 메모리(CMA)** 가 필요하다. 클린 설치 직후 기본값(약 8MB)은 부족하다.

### 8.1 부팅 설정 파일 찾기

보드/이미지에 따라 경로가 다르다. 아래 중 존재하는 파일을 연다.

```bash
ls -la /boot/extlinux/extlinux.conf 2>/dev/null
ls -la /boot/firmware/cmdline.txt 2>/dev/null
ls -la /boot/firmware/extlinux/extlinux.conf 2>/dev/null
```

### 8.2 extlinux.conf 인 경우

```bash
sudo nano /boot/extlinux/extlinux.conf
```

`append` 줄 **끝**에 공백 후 `cma=256M` 추가:

```text
append root=UUID=... rootwait rw ... cma=256M
```

### 8.3 cmdline.txt 인 경우

```bash
sudo nano /boot/firmware/cmdline.txt
```

한 줄 끝에 `cma=256M` 추가 (기존 내용 뒤 공백 구분).

### 8.4 적용

```bash
sudo reboot
```

재부팅 후 확인:

```bash
cat /proc/meminfo | grep -i Cma
cat /proc/cmdline
```

정상 예:

```text
CmaTotal:         262144 kB
... cma=256M ...
```

## 9. 작업용 계정 (선택)

이미지 기본 `ubuntu` 계정만으로도 02~04번을 진행할 수 있다. 별도 계정이 필요하면 **새로 생성**한다 (기존 장비에서 복사하지 않음).

```bash
sudo adduser devuser
sudo usermod -aG sudo,video,plugdev,render devuser
```

이후 문서의 `<USER>`를 `ubuntu` 또는 `devuser`로 바꾼다.

## 10. 트러블슈팅

| 증상 | 조치 |
|---|---|
| 부팅 안 됨 | SD 재굽기, 다른 SD·리더, 전원 5V/4A 확인 |
| 화면 없음 | HDMI·케이블 교체, 2~3분 추가 대기 |
| IP 없음 | LAN 연결, `ip link`, 공유기 DHCP 목록 확인 |
| CMA 미적용 | 부팅 설정 파일 경로 재확인, `sudo reboot` |

로그인 루프·백업 등 **기존 장비 복구**는 [OrangePI_LightDM_XFCE_무한잠금화면_해결방법.md](../OrangePI_LightDM_XFCE_무한잠금화면_해결방법.md), [OrangePI_전체시스템_백업_복구_방법.md](../OrangePI_전체시스템_백업_복구_방법.md) 참조.

## 11. 완료 확인

- [ ] 빈 SD에 OS 굽기·첫 부팅
- [ ] `sudo apt update && sudo apt upgrade` 완료
- [ ] `git`, `build-essential` 설치
- [ ] `hostname -I`로 IP 확인
- [ ] `/proc/cmdline`에 `cma=256M`, `CmaTotal` 약 256MB

## 12. 관련 링크

| 분류 | URL |
|---|---|
| OS | https://github.com/Joshua-Riek/ubuntu-rockchip/releases/tag/v2.4.0 |
| Tools | https://etcher.balena.io/ |

## 13. 다음 단계

→ [02_SSH_연결_및_설정.md](02_SSH_연결_및_설정.md): SSH 서버 설치 및 Windows 원격 접속

**[전원버튼 60초 타이머 끄기] gsettings set org.gnome.SessionManager logout-prompt false
