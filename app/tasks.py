from aiogram import html


async def products(bot, chat_id, ps, get_data):
    messages = []
    data = get_data(ps)

    for title, value, past_value in data:
        if value >= ps['minimal_total']:
            continue

        if value == 0:
            message = f'·{title}: {html.bold("n/a")}'
        else:
            message = f'·{title}: {html.bold(value)}'

        if past_value >= ps['minimal_total']:
            message = '·‼️ ' + message[1:]

        messages.append(message)

    if messages:
        await bot.send_message(
            chat_id,
            '\n'.join(messages),
        )
    else:
        await bot.send_message(
            chat_id,
            'There is not new info'
        )


async def employees(bot, chat_ids, es, get_data):
    data = get_data(es)

    for country, chat_id in chat_ids.items():
        messages = []
        for name, income in data[country].items():
            if income >= es['minimal_incomes'][country]:
                continue

            income = f'${income:.2f}'

            messages.append(f'·{name}: {html.bold(income)}')

        if messages:
            messages = '\n'.join(messages)
            await bot.send_message(
                chat_id,
                f'{country.upper()}:\n{messages}'
            )
        else:
            await bot.send_message(
                chat_id,
                f'{country.upper()}:\nThere is no new info'
            )
