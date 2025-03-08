import html


class EmailTemplate:
    template = '''
<div style="padding: 20px; background: #E5E7EB; font-family: 'Helvetica Neue', Arial, sans-serif; box-sizing: border-box;">
  <div style="max-width: 600px; margin: 0 auto; background: #ffffff; border-radius: 12px; overflow: hidden; box-shadow: 0 4px 12px rgba(0,0,0,0.1);">
    
    <div style="padding: 20px; background: linear-gradient(135deg, #667eea, #764ba2); text-align: center;">
      <span style="color: #ffffff; font-size: 14px;">NoTiX 自动通知</span>
    </div>
    
    <div style="padding: 40px;">
      <h1 style="color: #333333; font-size: 32px; margin-bottom: 10px;">{subject}</h1>

      <div style="height: 4px; width: 60px; background: #764ba2; margin-bottom: 20px; border-radius: 2px;"></div>
      <p style="color: #555555; font-size: 18px; margin-bottom: 20px;">{appellation}</p>
      <div style="color: #666666; font-size: 16px; line-height: 1.6;">{content}</div>
    </div>
    
    <div style="padding: 20px; background: #F3F4F6; text-align: center;">
      <span style="color: #888888; font-size: 12px;">
        连接世界，看见精彩 |
        <a href="https://github.com/Jyonn/NotificatorX" style="color: #667eea; text-decoration: none;">NoTiX</a>
      </span>
    </div>
  </div>
</div>>'''

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
