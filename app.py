from flask import Flask, render_template_string, request, jsonify

app = Flask(__name__)

EXCHANGE_RATES = {
    "USD": 1.0,
    "LKR": 300.0,
    "INR": 83.0,
    "GBP": 0.79,
    "EUR": 0.92,
    "AUD": 1.52,
    "CAD": 1.35,
    "JPY": 150.0,
    "SGD": 1.34,
    "AED": 3.67
}

FLAGS = {
    "USD": "🇺🇸", "LKR": "🇱🇰", "INR": "🇮🇳", "GBP": "🇬🇧",
    "EUR": "🇪🇺", "AUD": "🇦🇺", "CAD": "🇨🇦", "JPY": "🇯🇵",
    "SGD": "🇸🇬", "AED": "🇦🇪"
}

UI_TEMPLATE = """
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8" />
    <meta name="viewport" content="width=device-width, initial-scale=1.0"/>
    <title>Currency Converter</title>
    <link rel="preconnect" href="https://fonts.googleapis.com">
    <link href="https://fonts.googleapis.com/css2?family=DM+Mono:wght@400;500&family=Playfair+Display:wght@600&display=swap" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/@tabler/icons-webfont@latest/dist/tabler-icons.min.css"/>
    <style>
        *, *::before, *::after { box-sizing: border-box; margin: 0; padding: 0; }

        :root {
            --bg: #f4f6f9;
            --surface: #ffffff;
            --border: rgba(0,0,0,0.09);
            --border-focus: #378ADD;
            --text-primary: #111;
            --text-secondary: #555;
            --text-tertiary: #999;
            --accent: #185FA5;
            --accent-hover: #0C447C;
            --accent-light: #E6F1FB;
            --accent-mid: #B5D4F4;
            --result-bg: #f0f6fd;
            --radius: 10px;
            --radius-sm: 7px;
        }

        @media (prefers-color-scheme: dark) {
            :root {
                --bg: #111318;
                --surface: #1c1f26;
                --border: rgba(255,255,255,0.1);
                --border-focus: #378ADD;
                --text-primary: #f0f0f0;
                --text-secondary: #a0a0a0;
                --text-tertiary: #666;
                --accent: #5BA4E0;
                --accent-hover: #85B7EB;
                --accent-light: #0c2a42;
                --accent-mid: #1a3f5e;
                --result-bg: #0e1f31;
            }
        }

        body {
            background: var(--bg);
            font-family: 'DM Mono', monospace;
            min-height: 100vh;
            display: flex;
            align-items: center;
            justify-content: center;
            padding: 2rem 1rem;
        }

        .card {
            background: var(--surface);
            border: 0.5px solid var(--border);
            border-radius: var(--radius);
            padding: 2rem;
            width: 100%;
            max-width: 460px;
            box-shadow: 0 4px 24px rgba(0,0,0,0.06);
        }

        .header {
            display: flex;
            align-items: center;
            gap: 12px;
            padding-bottom: 1.5rem;
            border-bottom: 0.5px solid var(--border);
            margin-bottom: 1.75rem;
        }

        .logo {
            width: 42px; height: 42px;
            background: var(--accent-light);
            border-radius: var(--radius-sm);
            display: flex; align-items: center; justify-content: center;
            font-size: 20px;
            color: var(--accent);
        }

        .title {
            font-family: 'Playfair Display', serif;
            font-size: 19px;
            font-weight: 600;
            color: var(--text-primary);
        }

        .subtitle {
            font-size: 11px;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 0.06em;
            margin-top: 2px;
        }

        label {
            display: block;
            font-size: 10px;
            font-weight: 500;
            color: var(--text-tertiary);
            text-transform: uppercase;
            letter-spacing: 0.07em;
            margin-bottom: 6px;
        }

        .amount-wrap {
            position: relative;
            margin-bottom: 1.25rem;
        }

        .amount-icon {
            position: absolute;
            left: 12px;
            top: 50%;
            transform: translateY(-50%);
            color: var(--text-tertiary);
            font-size: 17px;
            pointer-events: none;
        }

        input[type="number"] {
            width: 100%;
            padding: 0.7rem 1rem 0.7rem 2.6rem;
            font-size: 20px;
            font-family: 'DM Mono', monospace;
            font-weight: 500;
            background: var(--surface);
            color: var(--text-primary);
            border: 0.5px solid var(--border);
            border-radius: var(--radius-sm);
            outline: none;
            transition: border-color 0.15s;
            appearance: none;
        }

        input[type="number"]:focus {
            border-color: var(--border-focus);
        }

        input[type="number"]::-webkit-inner-spin-button,
        input[type="number"]::-webkit-outer-spin-button { opacity: 0.4; }

        .selects-row {
            display: grid;
            grid-template-columns: 1fr 40px 1fr;
            gap: 8px;
            align-items: end;
            margin-bottom: 1.5rem;
        }

        select {
            width: 100%;
            padding: 0.6rem 0.75rem;
            font-size: 14px;
            font-family: 'DM Mono', monospace;
            font-weight: 500;
            background: var(--surface);
            color: var(--text-primary);
            border: 0.5px solid var(--border);
            border-radius: var(--radius-sm);
            outline: none;
            cursor: pointer;
            transition: border-color 0.15s;
        }

        select:focus { border-color: var(--border-focus); }

        .swap-btn {
            width: 40px; height: 40px;
            background: var(--bg);
            border: 0.5px solid var(--border);
            border-radius: var(--radius-sm);
            color: var(--text-secondary);
            display: flex; align-items: center; justify-content: center;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.15s, color 0.15s;
            flex-shrink: 0;
        }

        .swap-btn:hover {
            background: var(--accent-light);
            color: var(--accent);
            border-color: var(--accent-mid);
        }

        .convert-btn {
            width: 100%;
            padding: 0.8rem;
            background: var(--accent);
            color: #fff;
            border: none;
            border-radius: var(--radius-sm);
            font-size: 13px;
            font-family: 'DM Mono', monospace;
            font-weight: 500;
            letter-spacing: 0.07em;
            text-transform: uppercase;
            cursor: pointer;
            transition: background 0.15s, transform 0.1s;
            margin-bottom: 1.25rem;
        }

        .convert-btn:hover { background: var(--accent-hover); }
        .convert-btn:active { transform: scale(0.985); }

        .result {
            background: var(--result-bg);
            border: 0.5px solid var(--border);
            border-radius: var(--radius-sm);
            padding: 1.25rem;
            display: none;
            animation: fadeUp 0.22s ease;
        }

        .result.visible { display: block; }

        .result-from {
            font-size: 12px;
            color: var(--text-tertiary);
            margin-bottom: 4px;
        }

        .result-to {
            font-size: 28px;
            font-weight: 500;
            color: var(--accent);
            margin-bottom: 10px;
            letter-spacing: -0.01em;
        }

        .result-rate {
            font-size: 11px;
            color: var(--text-tertiary);
            padding-top: 10px;
            border-top: 0.5px solid var(--border);
        }

        .quick-pairs {
            display: flex;
            flex-wrap: wrap;
            gap: 6px;
            margin-top: 1.5rem;
            padding-top: 1.25rem;
            border-top: 0.5px solid var(--border);
        }

        .pill {
            font-size: 11px;
            font-family: 'DM Mono', monospace;
            padding: 4px 9px;
            background: var(--bg);
            border: 0.5px solid var(--border);
            border-radius: 100px;
            color: var(--text-secondary);
            cursor: pointer;
            transition: background 0.1s, color 0.1s;
        }

        .pill:hover {
            background: var(--accent-light);
            color: var(--accent);
            border-color: var(--accent-mid);
        }

        @keyframes fadeUp {
            from { opacity: 0; transform: translateY(6px); }
            to   { opacity: 1; transform: translateY(0); }
        }
    </style>
</head>
<body>
<div class="card">

    <div class="header">
        <div class="logo" aria-hidden="true"><i class="ti ti-currency-dollar"></i></div>
        <div>
            <div class="title">Currency Converter</div>
            <div class="subtitle">SOA · Live Exchange Rates</div>
        </div>
    </div>

    <div class="amount-wrap">
        <label for="amount">Amount</label>
        <i class="ti ti-coins amount-icon" aria-hidden="true"></i>
        <input type="number" id="amount" value="1" min="0" placeholder="0.00" />
    </div>

    <div class="selects-row">
        <div>
            <label for="from_currency">From</label>
            <select id="from_currency">
                {% for code, name in currencies %}
                <option value="{{ code }}" {% if code == 'USD' %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
            </select>
        </div>
        <button class="swap-btn" onclick="swapCurrencies()" title="Swap currencies" aria-label="Swap currencies">
            <i class="ti ti-arrows-exchange" aria-hidden="true"></i>
        </button>
        <div>
            <label for="to_currency">To</label>
            <select id="to_currency">
                {% for code, name in currencies %}
                <option value="{{ code }}" {% if code == 'LKR' %}selected{% endif %}>{{ name }}</option>
                {% endfor %}
            </select>
        </div>
    </div>

    <button class="convert-btn" onclick="convert()">
        <i class="ti ti-refresh" style="font-size:13px;vertical-align:-1px;margin-right:6px" aria-hidden="true"></i>
        Convert Now
    </button>

    <div id="resultBox" class="result" role="status" aria-live="polite">
        <p class="result-from" id="resultFrom"></p>
        <p class="result-to"   id="resultTo"></p>
        <p class="result-rate" id="resultRate"></p>
    </div>

    <div class="quick-pairs" id="quickPairs" aria-label="Quick currency pair shortcuts"></div>

</div>

<script>
    const FLAGS = {{ flags | tojson }};
    const QUICK = [['USD','LKR'],['EUR','USD'],['GBP','INR'],['USD','JPY'],['AUD','SGD']];

    const qWrap = document.getElementById('quickPairs');
    QUICK.forEach(([a, b]) => {
        const btn = document.createElement('button');
        btn.className = 'pill';
        btn.textContent = (FLAGS[a]||'') + a + ' → ' + (FLAGS[b]||'') + b;
        btn.onclick = () => {
            document.getElementById('from_currency').value = a;
            document.getElementById('to_currency').value   = b;
            convert();
        };
        qWrap.appendChild(btn);
    });

    async function convert() {
        const amount = parseFloat(document.getElementById('amount').value) || 0;
        const from   = document.getElementById('from_currency').value;
        const to     = document.getElementById('to_currency').value;

        const response = await fetch('/api/convert', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ amount, from, to })
        });

        const data = await response.json();
        const result = data.result;
        const rate   = data.rate;

        const fmt = v => v >= 1000
            ? v.toLocaleString(undefined, { minimumFractionDigits: 2, maximumFractionDigits: 2 })
            : parseFloat(v.toFixed(6)).toString();

        document.getElementById('resultFrom').textContent =
            `${FLAGS[from] || ''} ${amount.toLocaleString()} ${from}  =`;
        document.getElementById('resultTo').textContent =
            `${FLAGS[to] || ''} ${fmt(result)} ${to}`;
        document.getElementById('resultRate').textContent =
            `1 ${from} = ${fmt(rate)} ${to}  ·  1 ${to} = ${fmt(1 / rate)} ${from}`;

        const box = document.getElementById('resultBox');
        box.classList.remove('visible');
        void box.offsetWidth;
        box.classList.add('visible');
    }

    function swapCurrencies() {
        const f = document.getElementById('from_currency');
        const t = document.getElementById('to_currency');
        [f.value, t.value] = [t.value, f.value];
        convert();
    }

    convert();
</script>
</body>
</html>
"""


@app.route('/')
def index():
    currencies = [(code, f"{FLAGS.get(code, '')} {code}") for code in EXCHANGE_RATES]
    return render_template_string(UI_TEMPLATE, currencies=currencies, flags=FLAGS)


@app.route('/api/convert', methods=['POST'])
def convert_api():
    data = request.get_json()
    amount    = float(data['amount'])
    from_curr = data['from']
    to_curr   = data['to']

    amount_in_usd    = amount / EXCHANGE_RATES[from_curr]
    converted_amount = amount_in_usd * EXCHANGE_RATES[to_curr]
    rate             = EXCHANGE_RATES[to_curr] / EXCHANGE_RATES[from_curr]

    return jsonify({"result": converted_amount, "rate": rate})


if __name__ == '__main__':
    app.run(debug=True)