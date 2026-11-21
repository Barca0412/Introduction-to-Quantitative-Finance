# 一键订阅：每周 AI × 金融资讯的订阅服务

网站右上角的"一键订阅"按钮和站内看满 45 秒弹出的订阅卡片，都会把邮箱提交给这里的 `subscribe_server.py`。这个服务只用 Python 标准库加 SQLite，只监听 127.0.0.1:8731，由 nginx 把 `https://quant.hfthnu.com/api/subscribe/` 转发过来。

## 存了什么

数据库是 `~qgh/subscribe/subscribers.db`，只存这几项：

- 邮箱
- 关心的金融领域（最多 3 个）
- 状态：待确认、已订阅、已退订
- 两个随机令牌：一个用于确认，一个用于退订
- 时间

日志里不记邮箱，也不记 IP。

## 流程

1. 读者提交邮箱后，服务发一封确认信，读者点信里的确认链接才算订阅（双重确认）。确认链接 7 天内有效，只能用一次。
2. 每期周报里都带退订链接，一点就退订。这个链接同时支持邮箱客户端的"一键退订"（RFC 8058）。
3. 已经订阅的邮箱再提交一次，不会再发信，只更新关心的方向。提交后的回复也一样，不会透露这个邮箱以前订没订过。
4. 防机器人：同一个 IP 每小时最多提交 5 次；表单里有一个隐藏的陷阱字段，填了它的提交直接丢掉。

## 服务器上的文件

| 文件 | 说明 |
|---|---|
| `~qgh/subscribe/subscribe_server.py` | 服务本身，从仓库这个目录复制过去 |
| `~qgh/subscribe/config.env` | 配置文件，权限设成 600。发信密钥只写在这里，不进仓库 |
| `~qgh/subscribe/subscribers.db` | 订阅数据 |
| `/etc/systemd/system/iqf-subscribe.service` | 开机自启，由管理员安装，见 `subscribe.service` |

`config.env` 示例（没填 SMTP 时，信件会写进 `~/subscribe/outbox.txt`，不会真的发出去，方便先测试）：

```
SITE_URL=https://quant.hfthnu.com
MAIL_FROM=weekly@hfthnu.com
MAIL_FROM_NAME=AI × 金融周报
REPLY_TO=（收读者回信的邮箱）
SMTP_HOST=（发信服务给的 SMTP 地址）
SMTP_PORT=465
SMTP_USER=（发信服务给的用户名）
SMTP_PASS=（发信服务给的密码，只写在服务器上）
DOMAINS=asset-pricing,trading,portfolio-risk,derivatives,credit-banking,corporate-finance,fin-nlp,crypto-defi,macro-policy,insurance-household,market-structure
```

## nginx（加在 `/etc/nginx/conf.d/quant.hfthnu.com.conf` 的 HTTPS server 里）

```nginx
location /api/subscribe/ {
    proxy_pass http://127.0.0.1:8731;
    proxy_set_header Host $host;
    proxy_set_header X-Real-IP $remote_addr;
    client_max_body_size 8k;
    limit_except GET POST OPTIONS { deny all; }
}
```

## 常用操作

```bash
python3 ~/subscribe/subscribe_server.py count      # 各状态各有多少人
sudo systemctl status iqf-subscribe                 # 看服务是否在跑
journalctl -u iqf-subscribe -n 50                    # 最近日志
```

- 测试：`python3 -m unittest scripts/site/subscribe/test_subscribe_server.py`（测试会在 127.0.0.1 上开一个端口）。
- 读者要求删除数据：用 `sqlite3` 删掉对应那一行，并在回信里告知已删除。
- 每天的备份方式和 Umami 一样：放进 qgh 的 crontab，每天复制一份数据库，保留 14 天。
