---
marp: true
theme: default
paginate: true
header: 'Orange Pi 5 Max 교육자료'
footer: '02 SSH · IP'
---

# 02. SSH 연결 및 설정

**PowerShell** · **IP 접속** · SSH 서버 · 키

---

## 흐름

1. Orange Pi **IP 확인**
2. `ssh USER@IP` (비밀번호)
3. openssh-server 설치
4. ssh-keygen · 공개키 등록

---

## IP 확인

| 방법 | 위치 |
|------|------|
| HDMI | `hostname -I` |
| 공유기 | DHCP 목록 |

→ `<ORANGE_PI_IP>` 메모

---

## IP로 첫 로그인

```powershell
ssh ubuntu@192.168.0.42
```

- `yes` → host key
- 비밀번호: Server `ubuntu`

---

## SSH 서버

**Server**: 포함될 수 있음 → 확인

**Desktop**: HDMI 1회 설치

```bash
sudo apt install -y openssh-server
sudo systemctl enable --now ssh
```

---

## 키 · SCP

```powershell
# -C 는 키 주석(메모). 접속 IP 와 별개
ssh-keygen -t ed25519 -f "$env:USERPROFILE\.ssh\id_ed25519_orangepi" -C "ubuntu@192.168.0.42"
ssh -i ...\id_ed25519_orangepi ubuntu@192.168.0.42
```

---

## 완료

- [ ] IP 비밀번호·키 접속
- [ ] openssh-server
- [ ] VS Code Remote-SSH

→ **03 DX-M1**

---

## VS Code Remote-SSH

1. 확장: **Remote - SSH**
2. `F1` → Open SSH Configuration File
3. `Host orangepi5max` + IP + IdentityFile
4. `F1` → Connect to Host → Open Folder `/home/ubuntu`
