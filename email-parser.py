import os
import email
import email.policy
import json

with open('config.json', 'r') as fp:
    config = json.load(fp)
emails_dir = config['emails_dir']

MONTHS = {
    'Jan': 1, 'Feb': 2, 'Mar': 3, 'Apr': 4,
    'May': 5, 'Jun': 6, 'Jul': 7, 'Aug': 8,
    'Sep': 9, 'Oct': 10, 'Nov': 11, 'Dec': 12
}
def clean_date(date):
    day, month, year = date.split(' ')
    return '%s-%02d-%s' % (year, MONTHS[month], day)

def clean_price(price):
    price = price.strip()
    assert price[-3] == '.'
    price = price.replace(config['currency'], '')
    price = price.replace('.', '')
    return int(price)

def analyse_invoice(full_invoice):
    lines = full_invoice.split('\n')

    expect_apple_id = False
    expect_billed_to = False
    seen_total = False
    items = []
    running_total = 0

    for line in lines:
        if expect_apple_id:
            apple_id = line
            expect_apple_id = False
        elif expect_billed_to:
            billed_to = line
            expect_billed_to = False
        elif line == 'APPLE ID':
            expect_apple_id = True
        elif line == 'BILLED TO':
            expect_billed_to = True
        elif line.startswith('INVOICE DATE:'):
            invoice_date = clean_date(line[13:].strip())
        elif line.startswith('TOTAL:'):
            total = clean_price(line[6:].strip())
            seen_total = True
        elif config['total_keywords'] in line:
            split_card_total = clean_price(line[line.rfind(' '):])
        elif 'Store Credit Total' in line:
            split_credit_total = clean_price(line[line.rfind(' '):])
        elif seen_total and config['currency'] in line and not line.startswith(' '):
            name = line[:line.find('   ')]
            price = clean_price(line[line.rfind(' '):])
            running_total += price
            items.append((name, price))

    assert running_total == total

    obj = {'date': invoice_date, 'who': apple_id, 'items': items, 'card': 0, 'credit': 0}
    if billed_to == config['billed_to_combo']:
        # partial payment with store credit and with card
        obj['card'] = split_card_total
        obj['credit'] = split_credit_total
    elif billed_to.startswith(config['billed_to_prefix']):
        # fully paid by card
        obj['card'] = total
    elif billed_to == 'Store Credit':
        # fully paid by store credit
        obj['credit'] = total
    else:
        raise ValueError(billed_to)
    return obj


user_totals = {}

for name in os.listdir(emails_dir):
    if not name.endswith('.eml'):
        continue

    with open(f'{emails_dir}/{name}', 'rb') as fp:
        msg = email.message_from_binary_file(fp, policy=email.policy.default)
        assert msg.is_multipart()
        text_ver, html_ver = msg.get_payload()
        invoice = text_ver.get_content()

        bits = analyse_invoice(invoice)
        items = '; '.join([i[0] for i in bits['items']])
        who = bits['who']
        who = who[:who.index('@')]
        print(f"{bits['date']} | {bits['credit']:4d} | {bits['card']:4d} | {who:5s} | {items}")

        if bits['who'] in user_totals:
            user_totals[bits['who']] += bits['card']
        else:
            user_totals[bits['who']] = bits['card']


for key, value in user_totals.items():
    print(f'TOTAL: {key:40s} -> {value}')

