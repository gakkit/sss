#! /usr/local/bin/python3
# 用于用户的各类验证

# 发送验证码

import smtplib
import redis 
import random
import time

# 使用redis注意需要后台启动 redis-server。不同平台可能略有差异，但是redis的后天必须一直开启，类似数据库。

from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText


def set_redis(user_email):
    '''生成验证码'''
    r = redis.StrictRedis()
    code = str(random.uniform(0,1))[3:9]
    print(code, '*'*80) # 方便测试、代替实际发邮件
    while r.exists(user_email): # 不允许用户刷新后立刻重试
        time.sleep(1)
    r.set(user_email, code)
    r.expire(user_email, 120) # 2分钟以内输入有效（考虑到用户还要花时间登录邮箱）

def check_code(user_email, code):
    r = redis.StrictRedis()
    if r.exists(user_email):
        if code in str(r.get(user_email)):
            return 0
    return 1

def send_email(recipient, content_text, content_html):
    sender = "sss_service@sina.com"
    msg = MIMEMultipart('alternative')
    msg['Subject'] = "请验证您的邮箱地址来完成 SSS 账号设置"
    msg['From'] = 'sss_service@sina.com'
    msg['To'] = recipient
    # Create the body of the message (a plain-text and an HTML version).
    # Record the MIME types of both parts - text/plain and text/html.
    part1 = MIMEText(content_text, 'plain')
    part2 = MIMEText(content_html, 'html')
    # Attach parts into message container.
    # According to RFC 2046, the last part of a multipart message, in this case
    # the HTML message, is best and preferred.
    msg.attach(part1)
    msg.attach(part2)
    s = smtplib.SMTP('smtp.sina.com')
    print("login ...")
    s.login('sss_service', '') # 需要输入密码
    # sendmail function takes 3 arguments: sender's address, recipient's address
    # and message to send - here it is sent as one string.
    print("sending ...")
    s.sendmail(sender, recipient, msg.as_string())
    s.quit()

def main():
    recipient = 'ruxtain@foxmail.com'
    recipient = '571061858@qq.com'
    content_text = "您好，欢迎使用 SSS 服务，您正在进行邮箱验证，本次请求的验证码为：XXXXXX".replace('XXXXXX', '999999')
    content_html = """\
<!DOCTYPE html PUBLIC "-//W3C//DTD XHTML 1.0 Strict//EN" "http://www.w3.org/TR/xhtml1/DTD/xhtml1-strict.dtd">
<html xmlns="http://www.w3.org/1999/xhtml">
    <head>
        <!-- NAME: 1:3 COLUMN - BANDED -->
        <meta http-equiv="Content-Type" content="text/html; charset=UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>sss</title>
        <link rel="shortcut icon" href="/dist/images/favicon.ico">
        <!-- <link rel="stylesheet" type="text/css" href="/Tpl/Mail/templates/display/template.css"  /> -->
        <style>
        body {
            font-family: "Microsoft Yahei", "Simsun","Open Sans", "Helvetica Neue", Helvetica, Arial, sans-serif;
            color: #394263;
            font-size: 13px;
            word-break: break-word;
        }
        a{
            text-decoration: none;
        }
        p{
            margin: 0 0 5px;
            line-height: 1.6;
        }
        h1, h2, h3, h4, h5, h6 {
            margin:10px 0;font-weight: 300;
            line-height: 1.4;
        }
        h6{
            font-size: 13px;
        }
        h5{
            font-size: 14px;
        }
        h4{
            font-size: 18px;
        }
        h3{
            font-size: 24px;
        }
        h2{
            font-size: 30px;
        }
        h1{
            font-size: 36px;
        }

        img{
            max-width: 100%;
        }

        .layer-wrap .four-column .imageText .mcnCaptionRightTextContentContainer, .layer-wrap .four-column .imageText2 .mcnCaptionLeftTextContentContainer{
            width:45px;
        }

        .layer-wrap .four-column .imageText img, .layer-wrap .four-column .imageText2 img{

        }
        .layer-wrap .mcnImageCardBlockInner{
            padding-top: 10px;padding-right: 18px;padding-bottom: 9px;padding-left: 18px;
        }
        .layer-wrap .four-column .mcnImageCardBlockInner{
            padding:0;
        }
        .layer-wrap .three-column .mcnImageCardBlockInner{
            padding:0;
        }
        .layer-wrap .mcnImageCardTopContent{
            border: 1px solid #999999;
        }
        .layer-wrap .two-column .mcnImageCardTopContent{
            border:none;
        }
        .layer-wrap .three-column .mcnImageCardTopContent{
            border:none;
        }
        .layer-wrap .mcnImageCardBlock{
            border:1px solid #999;
        }
        .layer-wrap .four-column .mcnImageCardBlock, .layer-wrap .three-column .mcnImageCardBlock{
            border:none;
        }

        .layer-wrap .two-column .mcnImageCardBlockInner{
            padding:0;
        }
        .layer-wrap .two-column .mcnImageCardBlock{
            border:none;
        }

        @media only screen and (max-width: 480px){
                table{
                    width:100% !important;
                }
                table .setting-max-width{
                    margin: 0 !important;
                }
            }

            @media (min-width: 481px), not screen{
                table .setting-max-width{
                    width: 600px !important;
                }
            }

            @media only screen and (max-width: 480px){
                img[class=mcnImage]{
                    width:100% !important;
                }
            }
        
        </style>
    </head>
    <body leftmargin="0" marginwidth="0" topmargin="0" marginheight="0" offset="0" style="margin: 0;padding: 0;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;background-color:##edf0fc; width: 100% !important; ">
        <center><table align="center" border="0" cellpadding="0" cellspacing="0" width="100%" id="bodyTable" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;margin: 0;padding: 0;background-color: #edf0fc; width: 100% !important;">
                <tr>
                    <td align="center" valign="top" id="bodyCell" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;margin: 0;padding: 0;border-top: 0;height: 100% !important;width: 100% !important;"><!-- BEGIN TEMPLATE // --><table class="setting-max-width" border="0" cellpadding="0" cellspacing="0" width="600px" style="margin:10px 0 10px 0;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;background-color:#ffffff; width: 600px;">
                            <tr>
                                <td id="email-header" align="center" valign="top" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                    <!-- 头部开始 // -->
                                    <table border="0" cellpadding="0" cellspacing="0" class="text" width="100%" id="templateBody" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-top: 0;border-bottom: 0;background-color: transparent
     ;margin-top:0px;margin-bottom:0px;">
    <tr>
        <td align="center" valign="top" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="templateContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                <tr>
                    <td valign="top" class="bodyContainer" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                            <tbody class="mcnTextBlockOuter">
                                <tr>
                                    <td valign="top" class="mcnTextBlockInner" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextContentContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                            <tbody><tr>

                                                <td valign="top" class="mcnTextContent" style="padding-top:15px; padding-bottom:15px; padding-left:15px; padding-right:15px;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;text-align: left;font-size:13px;font-family:'Microsoft Yahei';color:rgb(51, 51, 51);">
                                                    <p><span style="font-size: 24px;">亲爱的用户：</span></p><p>您好！感谢您使用 SSS 服务，您正在进行邮箱验证，本次请求的验证码为：</p>                                                </td>
                                            </tr>
                                        </tbody></table>

                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>                                    <!-- 头部结束 // -->
                                </td>
                            </tr>
                            <tr>
                               <td id="email-body" align="center" valign="top" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                    <!-- 主体开始 // -->
                                    <table border="0" cellpadding="0" cellspacing="0" class="text" width="100%" id="templateBody" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-top: 0;border-bottom: 0;background-color: transparent
     ;margin-top:0px;margin-bottom:0px;">
    <tr>
        <td align="center" valign="top" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="templateContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                <tr>
                    <td valign="top" class="bodyContainer" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                            <tbody class="mcnTextBlockOuter">
                                <tr>
                                    <td valign="top" class="mcnTextBlockInner" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextContentContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                            <tbody><tr>

                                                <td valign="top" class="mcnTextContent" style="padding-top:15px; padding-bottom:15px; padding-left:15px; padding-right:15px;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;text-align: left;font-size:13px;font-family:'Microsoft Yahei';color:rgb(51, 51, 51);">
                                                    <p style="text-align: center;"><span style="font-size: 16px;"></span><span style="font-size: 18px; color: rgb(103, 147, 116);"><strong>XXXXXX</strong></span></p><p><span style="font-size: 18px; color: rgb(103, 147, 116);"><strong><br/></strong></span></p><p style="text-align: center;"><span style="font-size: 14px; color: rgb(165, 165, 165);">(为了保障您帐号的安全性，请在1小时内完成验证。)</span></p>                                                </td>
                                            </tr>
                                        </tbody></table>

                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>                                    <!-- 主体结束 // -->
                                </td>
                            </tr>
                            <tr>
                               <td id="email-footer" align="center" valign="top" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                    <!-- 尾部开始 // -->
                                    <table border="0" cellpadding="0" cellspacing="0" width="100%" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-top: 0;border-bottom: 0;background-color:     #fff ;margin-top:0px;margin-bottom:0px;">
    <tr>
        <td valign="top" class="preheaderContainer" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnDividerBlock" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                <tbody class="mcnDividerBlockOuter">
                    <tr>
                        <td class="mcnDividerBlockInner" style="padding-top:15px; padding-bottom:15px; padding-left:15px; padding-right:15px;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table class="mcnDividerContent" border="0" cellpadding="0" cellspacing="0" width="100%" style="border-top-width: 1px;border-top-style: dashed
                            ;border-top-color: #d4d4d4;border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                <tbody><tr>
                                    <td style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                        <span></span>
                                    </td>
                                </tr>
                            </tbody></table>
                        </td>
                    </tr>
                </tbody>
            </table>
        </td>
    </tr>
</table><table border="0" cellpadding="0" cellspacing="0" width="100%" id="templateColumns" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-top: 0;border-bottom: 0;">
    <tbody><tr class="layer-wrap" style="background:transparent
    ">
        <td align="left" valign="top" class="columnsContainer two-column"
    width="60%"style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="templateColumn" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
        <tbody><tr>
            <td valign="top" class="leftColumnContainer" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                    <tbody class="mcnTextBlockOuter">
                        <tr>
                            <td valign="top" class="mcnTextBlockInner" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextContentContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                    <tbody><tr>

                                        <td valign="top" class="mcnTextContent content-wrap" id="content-wrap" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;color: rgb(51, 51, 51);text-align: left;margin:">
                                             <table border="0" cellpadding="0" cellspacing="0" class="text" width="100%" id="templateBody" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-top: 0;border-bottom: 0;background-color: transparent
     ;margin-top:0px;margin-bottom:0px;">
    <tr>
        <td align="center" valign="top" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="templateContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                <tr>
                    <td valign="top" class="bodyContainer" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                            <tbody class="mcnTextBlockOuter">
                                <tr>
                                    <td valign="top" class="mcnTextBlockInner" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextContentContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                            <tbody><tr>

                                                <td valign="top" class="mcnTextContent" style="padding-top:15px; padding-bottom:15px; padding-left:15px; padding-right:15px;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;text-align: left;font-size:13px;font-family:'Microsoft Yahei';color:rgb(51, 51, 51);">
                                                    <p><span style="color:#7f7f7f">联系我们</span></p><p><span style="color: rgb(127, 127, 127);">电话：15084887874</span></p><p><span style="color: rgb(127, 127, 127);">网址：www.sss.com</span></p><p><span style="color: rgb(127, 127, 127);">地址：深圳市南山区XXX街道 518000</span></p>                                                </td>
                                            </tr>
                                        </tbody></table>

                                    </td>
                                </tr>
                            </tbody>
                        </table>
                    </td>
                </tr>
            </table>
        </td>
    </tr>
</table>                                        </td>
                                    </tr>
                                </tbody></table>

                            </td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
    </tbody></table>
</td><td align="left" valign="top" class="columnsContainer two-column"
    width="40%"style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="templateColumn" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
        <tbody><tr>
            <td valign="top" class="leftColumnContainer" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextBlock" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                    <tbody class="mcnTextBlockOuter">
                        <tr>
                            <td valign="top" class="mcnTextBlockInner" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table align="left" border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnTextContentContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                                    <tbody><tr>

                                        <td valign="top" class="mcnTextContent content-wrap" id="content-wrap" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;color: rgb(51, 51, 51);text-align: left;margin:">
                                             <table border="0" cellpadding="0" cellspacing="0" width="100%" class="image" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;border-top: 0;border-bottom: 0;background-color: transparent
     ;margin-top:0px;margin-bottom:0px;">
    <tr>
        <td valign="top" class="headerContainer" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;"><table border="0" cellpadding="0" cellspacing="0" width="100%" class="mcnImageBlock" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;">
                <tbody class="mcnImageBlockOuter">
                    <tr>
                        <td valign="top" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;" class="mcnImageBlockInner"><table align="left" width="100%" border="0" cellpadding="0" cellspacing="0" class="mcnImageContentContainer" style="border-collapse: collapse;mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;table-layout:fixed;word-wrap:break-word;word-break;break-all;">
                                <tbody>
                                    <tr>
                                        <td class="mcnImageContent" valign="top" style="mso-table-lspace: 0pt;mso-table-rspace: 0pt;-ms-text-size-adjust: 100%;-webkit-text-size-adjust: 100%;" align="center">
                                            <div style="padding-top:15px; padding-bottom:15px; padding-left:15px; padding-right:15px;"><!-- 用路径判断是否为默认图片 --><img src="https://dn-lingxi-uploads.qbox.me/uploadify/20170317/58cb86a958d5e.png-mailtemplate" width="100%" style="padding-bottom: 0;display: inline-block !important;vertical-align: bottom;border: 0;outline: none;text-decoration: none;-ms-interpolation-mode: bicubic;min-width: 10px" class="mcnImage"></div></td>
                                    </tr>
                                </tbody>
                            </table>
                        </td>
                    </tr>
                </tbody>
            </table>
        </td>
    </tr>
</table>                                        </td>
                                    </tr>
                                </tbody></table>

                            </td>
                        </tr>
                    </tbody>
                </table>
            </td>
        </tr>
    </tbody></table>
</td>    </tr>
</tbody></table>                                    <!-- 尾部结束 // -->
                                </td>
                            </tr>
                        </table>
                        <!-- // END TEMPLATE -->
                    </td>
                </tr>
            </table>
        </center>
        <div style="max-width: 600px; margin: 0 auto;">
        <div class="preview" id="preview"><hr style="margin: 0px;height: 1px;border-left: 1px;border-right: 0px;border-top: 0px;max-width: 300px;color: #eee;"/></div>
        <!-- {__LINGXI_FOOTER__} -->
        </div>
        <!-- {__MAX_WIDTH__:{$max_width}} -->
    </body>
    <script type="text/javascript">
        if (typeof jQuery == 'undefined') {
            loadJqueryLib();
            boundButtonWidth();
        }

        function loadJqueryLib() {
            document.write("<script src=\"https://s.lingxi360.com/jquery/1.11.3/jquery.min.js\" type=\"text/javascript\"><\/script>");
        }

        function boundButtonWidth () {
          var html = '<script>' +
            '$(function () {' +
            '  var $body = $("body");' +
            '  $(".btn-sm").each(function () {' +
            '    var $button = $(this);' +
            '    if ($button.width() > $body.width() - 30) {' +
            '      $button.css("width", "100%");' +
            '    }' +
            '  });' +
            '})' +
            '<\/script>';
          document.write(html);
        }
    </script>
</html>
    """.replace('XXXXXX', '999999')
    send_email(recipient, content_text, content_html)

if __name__ == '__main__':
    main()