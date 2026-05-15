# Copilot install

> Source: /spaces/CARSFW/pages/6973497990/Copilot+install
> Last modified: 2026-04-09T04:12:24.000+02:00

---

一、申请权限

在 one idm 中申请以下权限

IDM2BCD_BDC_Githubcom_CoPilot

等权限审批之后你会接收到三封邮件，分别为

1. Bosch Identity Management (Please do not reply) <Identity.Manager@ de.bosch.com > //  assign access right
2. GitHub <noreply@ github.com > //   join bosch copilot
3. Bosch Identity Management (Please do not reply) <Identity.Manager@ de.bosch.com > // Create account

我们主要使用第2封邮件。

二、注册 git hub 账户

1. 修改浏览器 proxy ，改为 hk 。
2. 登录git hub官网 ，连接如下： https://github.com/
3. 创建账户

3.1 输入公司的邮箱，例如 XXX@cn.bosch.com

3.2 输入用户名， 自己起个 github 账号名

3.3 输入密码 字母 + 数字 + 特殊符号，字母要有一个大写

3.4 点击 create account

1. 使用账户 密码登录
2. 点击接收到的 join bosch copilot 邮件
3. 添加一个账号， NT@bosch.com ；之后会接收到一个 verify 的邮件，去点击邮件进行验证；
4. 再次点击 join bosch copilot 邮件，进行二次验证，会出现一个二维码，此时需要执行下面的步骤
5. 在自己手机上安装 authenticator app ，点击 已验证 ID, 点击扫描 QR 码，手机上会出现 github ，点击 github ，

获取验证码，将验证码输入到第 7 步；

三、打开 visual studio code 软件

1. 在左侧点击 extention 按钮，搜索 GitHub copilot ，然后点击安装，顺便把自动更新勾上；

安装完之后会在界面的右侧出现一个 chat ；下面会有 agent 以及 GPT 等字样；

2. 出现上述这些， copilot 已经安装完毕，可以进行使用；

3. 如果安装好copilot，但是看不到模型存在，请检查下面两个方面：

3.1 看是否已经点击 join bosch copilot 这个邮件，验证是否成功；

3.2 如果3.1完成，还是没有出现，就检查一下vscode软件的账户登录，是不是git hub官网的登录账户。

3.3 在登录vscode的账户时，会跳转到网页进行授权，如果出现以下图片，点击cancel即可。

![](../../_images/Copilot%20install/%E5%9B%BE%E5%83%8F.png)

注意，如果需要更新则需要临时管理员权限；
