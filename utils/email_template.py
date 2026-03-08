import html

from utils.i18n import (
    NotifyLocales,
    get_brand_name,
    get_product_name,
    normalize_locale,
    translate,
)


class EmailTemplate:
    template = '''
<div style="margin:0; padding:24px 0; background:#f4f6f8; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',Roboto,Helvetica,Arial,sans-serif; -webkit-text-size-adjust:100%%; text-size-adjust:100%%;">
  <style>
    @media screen and (max-width: 600px) {{
      .mx-wrap {{ width:100%% !important; max-width:100%% !important; }}
      .mx-card-pad {{ padding:18px 16px !important; }}
      .mx-body-pad {{ padding:18px 16px !important; }}
      .mx-footer-pad {{ padding:14px 16px !important; }}
      .mx-brand {{ font-size:14px !important; }}
      .mx-subject {{ font-size:24px !important; line-height:1.4 !important; }}
      .mx-greeting {{ font-size:17px !important; line-height:1.7 !important; }}
      .mx-content {{ font-size:17px !important; line-height:1.75 !important; }}
      .mx-footer {{ font-size:13px !important; line-height:1.7 !important; }}
      .mx-btn {{ font-size:16px !important; padding:12px 18px !important; }}
    }}
  </style>
  <table role="presentation" width="100%%" cellspacing="0" cellpadding="0" border="0" style="border-collapse:collapse;">
    <tr>
      <td align="center">
        <table role="presentation" width="680" cellspacing="0" cellpadding="0" border="0" class="mx-wrap" style="max-width:680px; width:100%%; border-collapse:collapse;">
          <tr>
            <td style="padding:0 16px;">
              <table role="presentation" width="100%%" cellspacing="0" cellpadding="0" border="0" style="background:#ffffff; border:1px solid #e6e9ed; border-radius:12px; border-collapse:separate;">
                <tr>
                  <td class="mx-card-pad" style="padding:22px 26px; border-bottom:1px solid #eef1f4;">
                    <div class="mx-brand" style="font-size:15px; color:#64748b; letter-spacing:0.2px;">{brand_line}</div>
                    <div class="mx-subject" style="margin-top:8px; font-size:26px; line-height:1.35; color:#0f172a; font-weight:600;">{subject}</div>
                  </td>
                </tr>
                <tr>
                  <td class="mx-body-pad" style="padding:28px 26px;">
                    {greeting_block}
                    <div class="mx-content" style="font-size:16px; line-height:1.75; color:#1f2937; word-break:break-word;">{content_html}</div>
                    {action_block}
                  </td>
                </tr>
                <tr>
                  <td class="mx-footer mx-footer-pad" style="padding:16px 26px; border-top:1px solid #eef1f4; font-size:13px; line-height:1.7; color:#6b7280;">
                    <div>{sent_by_line}</div>
                    {footer_block}
                  </td>
                </tr>
              </table>
            </td>
          </tr>
        </table>
      </td>
    </tr>
  </table>
</div>'''

    @staticmethod
    def text_to_html(content):
        return html.escape(str(content)).replace('\n', '<br>')

    def __init__(
            self,
            subject,
            content_html,
            recipient_name=None,
            action_url=None,
            action_text=None,
            footer_note=None,
            sender_name=None,
            locale=NotifyLocales.DEFAULT,
            brand_name=None,
            product_name=None,
    ):
        self.locale = normalize_locale(locale)
        self.subject = html.escape(str(subject))
        self.content_html = str(content_html)
        self.recipient_name = recipient_name
        self.action_url = action_url
        self.action_text = action_text
        self.footer_note = footer_note
        self.brand_name = html.escape(str(brand_name or get_brand_name(self.locale)))
        self.product_name = html.escape(str(product_name or get_product_name(self.locale)))
        self.sender_name = html.escape(str(sender_name or html.unescape(self.brand_name)))

    def build_greeting_block(self):
        if not self.recipient_name:
            return ''
        greeting_text = translate(
            self.locale,
            'mail.greeting',
            recipient_name=html.escape(str(self.recipient_name)),
        )
        return (
            '<div class="mx-greeting" style="margin:0 0 14px 0; font-size:16px; line-height:1.7; color:#334155;">'
            f'{greeting_text}'
            '</div>'
        )

    def build_action_block(self):
        if not self.action_url:
            return ''
        action_text = self.action_text or translate(self.locale, 'mail.action.view_details')
        return (
            '<div style="margin-top:24px;">'
            f'<a href="{html.escape(str(self.action_url), quote=True)}" '
            'class="mx-btn" style="display:inline-block; background:#2563eb; color:#ffffff; text-decoration:none; '
            'font-size:15px; padding:11px 17px; border-radius:8px;">'
            f'{html.escape(str(action_text))}</a>'
            '</div>'
        )

    def build_footer_block(self):
        if not self.footer_note:
            return ''
        return f'<div style="margin-top:4px;">{html.escape(str(self.footer_note))}</div>'

    def build_sent_by_line(self):
        return translate(self.locale, 'mail.footer.sent_by', sender_name=html.unescape(self.sender_name))

    def build_brand_line(self):
        return f'{html.unescape(self.brand_name)} · {html.unescape(self.product_name)}'

    def export(self):
        return self.template.format(
            subject=self.subject,
            content_html=self.content_html,
            greeting_block=self.build_greeting_block(),
            action_block=self.build_action_block(),
            sent_by_line=html.escape(self.build_sent_by_line()),
            brand_line=html.escape(self.build_brand_line()),
            footer_block=self.build_footer_block(),
        )
