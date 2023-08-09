import textwrap

import requests


def main():
    token = "<token>"
    chat_id = "<chat-id>"
    parse_mode = "HTML"
    url = f"""https://api.telegram.org/bot{token}/sendMessage"""

    text = textwrap.dedent(
        f"""\
        <b>PnL</b>: <code>        0.00% 🟡</code>
        <b>Wallet</b>:
        <code> Wo:        1.282573</code>
        <code> Wp:        1.282573</code>
        <code> Wc:        0.000000</code>
        <code> Wc/Wo:     0.00% 🟡</code>
        <code> Wc/Wp:     0.00% 🟡</code>
        <b>Token</b>:
        <code> To:        0.000420</code>
        <code> Tp:        0.000420</code>
        <code> Tc:        0.000000</code>
        <code> Tc/To:     0.00% 🟡</code>
        <code> Tc/Tp:     0.00% 🟡</code>
        <b>Price</b>:
        <code> Expected:  0.000013</code>
        <code> Last fill: 0.000420</code>
        <code> Middle:    0.000010</code>
        <code> Adjusted:  0.156742</code>
        <b>Balance</b>:
        <code> BASE:     2975</code>
        <code> QUOTE:      0.032132</code>
        <b>Orders</b>:
        <code> Replaced:  1</code>
        <code> Canceled:  0</code>
        """
    )

    parameters = {
        "chat_id": chat_id,
        "parse_mode": parse_mode,
        "text": text
    }
    response = requests.get(url=url, params=parameters)
    json = response.json()

    print(json)


if __name__ == "__main__":
    main()
