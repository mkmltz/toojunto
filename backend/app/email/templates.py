from html import escape


def build_text_content(
    title: str,
    message: str,
    action_url: str | None = None,
    action_label: str | None = None,
) -> str:
    parts = [title, "", message]
    if action_url and action_label:
        parts.extend(["", f"{action_label}: {action_url}"])
    parts.extend(["", "TooJunto — sua caixinha, organizada e transparente."])
    return "\n".join(parts)


def build_html_content(
    title: str,
    message: str,
    action_url: str | None = None,
    action_label: str | None = None,
) -> str:
    safe_title = escape(title)
    safe_message = escape(message).replace("\n", "<br>")
    action = ""
    if action_url and action_label:
        action = f"""
            <tr>
              <td style="padding:8px 24px 24px">
                <a href="{escape(action_url, quote=True)}"
                   style="background:#2563eb;color:#ffffff;display:inline-block;
                          font-weight:600;padding:12px 18px;text-decoration:none;
                          border-radius:8px">
                  {escape(action_label)}
                </a>
              </td>
            </tr>"""

    return f"""<!doctype html>
<html lang="pt-BR">
  <head>
    <meta charset="utf-8">
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <title>{safe_title}</title>
  </head>
  <body style="margin:0;background:#f3f4f6;font-family:Arial,sans-serif;color:#172033">
    <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
           style="background:#f3f4f6;padding:24px 12px">
      <tr>
        <td align="center">
          <table role="presentation" width="100%" cellspacing="0" cellpadding="0"
                 style="background:#ffffff;border-radius:12px;max-width:560px">
            <tr>
              <td style="padding:24px 24px 8px;font-size:14px;font-weight:700;
                         color:#2563eb">TooJunto</td>
            </tr>
            <tr>
              <td style="padding:8px 24px;font-size:24px;font-weight:700">
                {safe_title}
              </td>
            </tr>
            <tr>
              <td style="padding:8px 24px 20px;font-size:16px;line-height:1.5">
                {safe_message}
              </td>
            </tr>
            {action}
            <tr>
              <td style="padding:16px 24px 24px;font-size:12px;color:#667085">
                TooJunto — sua caixinha, organizada e transparente.
              </td>
            </tr>
          </table>
        </td>
      </tr>
    </table>
  </body>
</html>"""
