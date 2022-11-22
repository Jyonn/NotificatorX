import html


class EmailTemplate:
    template = '''
    <div style="padding:0;margin:0;box-sizing:border-box;width:100%;display:flex;justify-content:center;background:#F8F8F8;">
     <div style="width:500px;position:relative;">
      <div style="height:50px;line-height:50px;width:100%;">
       <div style="color:#999999;padding:0 20px;font-size:12px;">以下内容为NoTiX自动发送</div>
      </div>
      <div>
       <div style="position:relative;border-radius:10px;background:white;padding:50px;">
        <div style="color:black;font-size:36px;padding-bottom:20px;">{subject}</div>
        <div style="color:#888888;font-size:16px;">{appellation}</div>
        <div style="color:#888888;font-size:16px;padding:10px 20px">{content}</div>
       </div>
      </div>
      <div style="height:50px;line-height:50px;width:100%;">
       <div style="color:#999999;padding:0 20px;font-size:12px;">连接世界，看见精彩 | <a href="https://github.com/Jyonn/NotificatorX" style="color:#FFB500;">NoTiX</a></div>
      </div>
     </div>
    </div>'''

    def __init__(self, subject, appellation, content):
        self.subject = html.escape(subject)
        self.appellation = html.escape(appellation)
        self.content = html.escape(content)

    def export(self):
        return self.template.format(
            subject=self.subject,
            appellation=self.appellation,
            content=self.content
        )
