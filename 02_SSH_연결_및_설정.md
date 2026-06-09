# 02. SSH 연결 및 설정

## 1. 목적

01번에서 부팅한 Orange Pi에 **IP 주소로 원격 접속**할 수 있게 하고, Windows **PowerShell(OpenSSH)** 에서 SSH 서버 설치·키 등록·SCP까지 구성한다.

## 2. 시작 상태

| 항목 | 이 단계 시작 시 |
|---|---|
| OS | 01번 완료 (Ubuntu Rockchip 부팅·LAN 연결) |
| Orange Pi IP | **아직 모름** (확인 필요) |
| SSH 서버 | **미설치 또는 미확인** |
| SSH 키 | Windows·Orange Pi 모두 **없음** |

### 2.1 OS 이미지별 SSH 상태

| 이미지 | SSH 서버 | 첫 접속 방법 |
|---|---|---|
| **Ubuntu Server** | 보통 **openssh-server 포함·기동** | PowerShell에서 IP로 바로 `ssh` 가능 |
| **Ubuntu Desktop** | 기본 **미설치**일 수 있음 | HDMI로 1회 로그인 → SSH 설치 → IP 접속 |

저장소 `ssh_keys/`는 **다른 PC용 예시**이며, 이 교육에서는 Windows에서 **새 키를 생성**한다.

## 3. 사전 조건

- [01_OrangePi5Max_OS_설치.md](01_OrangePi5Max_OS_설치.md) 완료
- Orange Pi와 Windows PC가 **같은 LAN**
- Windows **OpenSSH Client** (Windows 10/11 기본 포함, 없으면 설정 → 선택적 기능에서 설치)
- 작업 계정: `<USER>` (Server: `ubuntu` / Desktop: 마법사에서 생성한 이름)

## 4. Orange Pi IP 주소 확인

PowerShell에서 `ssh <USER>@<IP>` 접속하려면 Orange Pi의 **LAN IP**(예: `192.168.0.42`)가 필요하다.

### 4.1 Orange Pi에서 직접 확인 (HDMI, 가장 확실)

Orange Pi 로컬 터미널:

```bash
hostname -I
ip -4 addr show
```

첫 번째 주소(보통 `192.168.x.x`)를 메모 → `<ORANGE_PI_IP>`

### 4.2 공유기 DHCP 목록

공유기 관리 페이지 → 연결된 장치 / DHCP Client 목록에서 Orange Pi(또는 `ubuntu`, MAC 주소) 항목의 IP 확인.

### 4.3 Windows PowerShell에서 연결 테스트

IP를 알았으면:

```powershell
ping <ORANGE_PI_IP>
Test-NetConnection <ORANGE_PI_IP> -Port 22
```

응답이 없으면 LAN 케이블·공유기·Orange Pi 전원을 확인한다.

## 5. Windows — IP로 첫 접속 (비밀번호 로그인)

PowerShell:

```powershell
ssh <USER>@<ORANGE_PI_IP>
```

예 (Ubuntu Server):

```powershell
ssh ubuntu@192.168.0.42
```

| 항목 | 값 |
|---|---|
| `<USER>` | Server: `ubuntu` / Desktop: 설정한 사용자 |
| `<ORANGE_PI_IP>` | 4절에서 확인한 IP |
| 비밀번호 | Server: `ubuntu` (변경 권장) / Desktop: 설정한 비밀번호 |

최초 접속:

```text
Are you sure you want to continue connecting (yes/no/[fingerprint])? yes
```

비밀번호 입력 후 프롬프트가 Orange Pi(`ubuntu@...`)이면 **IP 로그인 성공**.

```powershell
exit
```

### 5.1 Connection refused 일 때

SSH 서버가 없거나 꺼져 있다. **6절**로 HDMI 또는 원격으로 `openssh-server`를 설치한다.

## 6. Orange Pi — SSH 서버 설치

### 6.1 경로 A: IP 접속이 이미 되는 경우 (Server 이미지 등)

PowerShell에서 접속한 뒤 Orange Pi 셸에서:

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
sudo systemctl status ssh
sudo ss -lntp | grep :22
```

이미 동작 중이면 `status`만 확인하고 7절로 진행.

### 6.2 경로 B: IP 접속이 안 되는 경우 (Desktop, SSH 미설치)

Orange Pi **HDMI + 키보드**로 로컬 로그인 후:

```bash
sudo apt update
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
hostname -I
```

설치 후 PowerShell에서 **5절** IP 접속을 재시도:

```powershell
ssh ubuntu@192.168.0.42
```

### 6.3 방화벽 (해당 시)

```bash
sudo ufw allow 22/tcp
sudo ufw status
```

## 7. Windows — SSH 키 새로 생성

PowerShell:

```powershell
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\id_ed25519_orangepi" -C "<USER>@orangepi5max"
```

공개키 확인:

```powershell
Get-Content "$env:USERPROFILE\.ssh\id_ed25519_orangepi.pub"
```

## 8. 공개키 등록 (IP 접속)

비밀번호 로그인이 되는 상태에서 PowerShell:

```powershell
type "$env:USERPROFILE\.ssh\id_ed25519_orangepi.pub" | ssh <USER>@<ORANGE_PI_IP> "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

### 수동 등록 (HDMI)

Orange Pi에서:

```bash
mkdir -p ~/.ssh && chmod 700 ~/.ssh
nano ~/.ssh/authorized_keys
# Windows .pub 내용을 한 줄로 붙여넣기
chmod 600 ~/.ssh/authorized_keys
```

## 9. 키 기반 IP 접속 확인

```powershell
ssh -i "$env:USERPROFILE\.ssh\id_ed25519_orangepi" <USER>@<ORANGE_PI_IP>
```

비밀번호 없이 접속되면 성공.

## 10. Windows SSH config (선택)

`%USERPROFILE%\.ssh\config`:

```text
Host orangepi5max
    HostName <ORANGE_PI_IP>
    User <USER>
    IdentityFile ~/.ssh/id_ed25519_orangepi
    IdentitiesOnly yes
```

```powershell
ssh orangepi5max
```

## 11. mDNS (선택)

Orange Pi (SSH 접속 중):

```bash
sudo hostnamectl set-hostname orangepi5max
sudo apt install -y avahi-daemon
sudo systemctl enable --now avahi-daemon
```

PowerShell:

```powershell
ping orangepi5max.local
ssh -i "$env:USERPROFILE\.ssh\id_ed25519_orangepi" <USER>@orangepi5max.local
```

자세한 설정: [OrangePI5MAX_네트워크_ID_설정법.md](../OrangePI5MAX_네트워크_ID_설정법.md)

## 12. 파일 전송 (SCP)

### Windows → Orange Pi

```powershell
scp -i "$env:USERPROFILE\.ssh\id_ed25519_orangepi" .\local_file.txt <USER>@<ORANGE_PI_IP>:~/
```

### Orange Pi → Windows

```powershell
scp -i "$env:USERPROFILE\.ssh\id_ed25519_orangepi" <USER>@<ORANGE_PI_IP>:~/remote_file.txt .
```

## 13. 보안 강화 (키 등록 확인 후)

Orange Pi:

```bash
sudo nano /etc/ssh/sshd_config
```

```text
PasswordAuthentication no
PubkeyAuthentication yes
PermitRootLogin no
```

```bash
sudo systemctl restart ssh
```

**주의:** 키 접속을 먼저 확인한 뒤 비밀번호 로그인을 끈다.

## 14. 트러블슈팅

| 증상 | 조치 |
|---|---|
| Connection refused | 6절 openssh-server 설치, `systemctl status ssh` |
| IP를 모름 | 4.1 HDMI `hostname -I`, 공유기 DHCP |
| Permission denied (publickey) | `authorized_keys`, chmod 600, `-i` 키 경로 |
| Host key changed | `ssh-keygen -R <ORANGE_PI_IP>` |
| ping 안 됨 | LAN 케이블, 같은 공유기/Wi-Fi 대역 확인 |

## 15. 작업 흐름 요약

```text
[Orange Pi] LAN 연결, IP 확인 (4절)
       |
[Windows] ssh <USER>@<IP> 비밀번호 로그인 (5절)
       |
[Orange Pi] openssh-server 설치·확인 (6절)
       |
[Windows] ssh-keygen → 공개키 등록 (7~8절)
       |
[Windows] ssh -i ... <USER>@<IP> 키 접속 (9절)
```

## 16. 완료 확인

- [ ] `<ORANGE_PI_IP>` 확인
- [ ] PowerShell `ssh <USER>@<IP>` **비밀번호** 로그인 성공
- [ ] `openssh-server` 설치·22번 포트 리슨
- [ ] Windows **새 ed25519 키** 생성·등록
- [ ] **키로 IP 접속** 및 `scp` 성공

## 17. 다음 단계

→ [03_DX-M1_NPU_드라이버_설치_및_테스트.md](03_DX-M1_NPU_드라이버_설치_및_테스트.md): DeepX M1 장착 및 dx-all-suite 설치
