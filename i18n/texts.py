from __future__ import annotations

# Ключи одинаковы для ru/uk. Плейсхолдеры: {name}, {n}, {seconds}, ...

TEXTS: dict[str, dict[str, str]] = {
    "ru": {
        # roles
        "role.civilian.title": "Мирный житель",
        "role.civilian.desc": "Ночью спит. Днём ищет мафию и голосует.",
        "role.don.title": "Дон",
        "role.don.desc": "Глава мафии. Ночью вместе с семьёй выбирает жертву. Его голос решающий.",
        "role.mafia.title": "Мафия",
        "role.mafia.desc": "Член семьи. Ночью выбирает жертву вместе с Доном.",
        "role.commissioner.title": "Комиссар",
        "role.commissioner.desc": "Ночью может проверить роль игрока или выстрелить.",
        "role.sergeant.title": "Сержант",
        "role.sergeant.desc": "Узнаёт о проверках комиссара. При гибели комиссара становится им.",
        "role.doctor.title": "Доктор",
        "role.doctor.desc": "Ночью спасает одного игрока. Себя — только один раз за игру.",
        "role.maniac.title": "Маньяк",
        "role.maniac.desc": "Убивает каждую ночь. Победа — уничтожить всех остальных.",
        "role.mistress.title": "Любовница",
        "role.mistress.desc": "Отвлекает игрока на ночь и следующий день.",
        "role.lawyer.title": "Адвокат",
        "role.lawyer.desc": "Выбирает подзащитного. Проверка комиссара покажет «мирный».",
        "role.suicide.title": "Самоубийца",
        "role.suicide.desc": "Побеждает только если его казнят дневным голосованием.",
        "role.homeless.title": "Бомж",
        "role.homeless.desc": "Видит ночные визиты: кто к кому ходил.",
        "role.lucky.title": "Счастливчик",
        "role.lucky.desc": "При покушении может выжить благодаря удаче.",
        "role.kamikaze.title": "Камикадзе",
        "role.kamikaze.desc": "При повешении может утащить с собой одного игрока.",
        "role.card": "Ваша роль: {emoji} <b>{title}</b>\n\n{desc}",
        "role.civilian.short": "👤 Мирный житель",
        "visit.mistress": "Любовница",
        "visit.lawyer": "Адвокат",
        "visit.mafia": "Мафия",
        "visit.maniac": "Маньяк",
        "visit.commissioner": "Комиссар",
        "visit.doctor": "Доктор",
        # private start
        "start.welcome": (
            "🤵🏻 <b>Мафия</b>\n\n"
            "Бесплатный бот для игры в Мафию в Telegram-чатах.\n\n"
            "Добавьте меня в группу и сделайте администратором "
            "(удаление сообщений + ограничение участников), затем напишите /game"
        ),
        "rules.text": (
            "🎭 <b>Мафия — правила</b>\n\n"
            "Игра в групповом чате. Ночью тишина: действия в личке с ботом.\n"
            "Днём живые обсуждают и голосуют, мёртвые молчат.\n\n"
            "<b>Победа</b>\n"
            "🏙️ Мирные — уничтожены мафия и маньяк\n"
            "😎 Мафия — мафиози ≥ остальных\n"
            "🔪 Маньяк — остался один / убил всех\n"
            "💀 Самоубийца — казнён дневным голосованием\n\n"
            "Команды в чате:\n"
            "/game — создать набор\n"
            "/stop — остановить игру (хост/админ)\n"
            "/players — список игроков\n"
            "/skip — досрочно перейти к следующей фазе (хост)\n"
            "/lang — язык чата (только владелец)"
        ),
        "btn.add_to_chat": "➕ Добавить бота в чат",
        "btn.rules": "📖 Правила",
        "btn.lang": "🌐 Язык",
        "btn.lang_ru": "🇷🇺 Русский",
        "btn.lang_uk": "🇺🇦 Українська",
        "lang.choose_private": "Выберите язык бота (личные сообщения):",
        "lang.choose_chat": "Выберите язык чата (сообщения в группе):",
        "lang.set_private": "✅ Язык бота: {lang_name}",
        "lang.set_chat": "✅ Язык чата: {lang_name}",
        "lang.name.ru": "Русский",
        "lang.name.uk": "Українська",
        "lang.only_owner": "Язык чата может менять только владелец группы.",
        "lang.current_private": "Ваш язык в боте: <b>{lang_name}</b>",
        "lang.current_chat": "Язык этого чата: <b>{lang_name}</b>",
        # lobby / group
        "btn.join": "✅ Присоединиться",
        "btn.leave": "🚪 Выйти",
        "btn.start_game": "▶️ Начать игру",
        "btn.cancel": "✖️ Отменить",
        "lobby.title": "🎭 <b>Набор в Мафию</b>",
        "lobby.players": "Игроки ({n}):",
        "lobby.empty": "— пока никого —",
        "lobby.hint": "Хост: нажмите «Начать игру», когда все готовы.",
        "lobby.need": "Нужно от {min} до {max} игроков.",
        "bot.need_admin": (
            "Сделайте бота администратором чата с правами:\n"
            "• удаление сообщений\n"
            "• ограничение участников"
        ),
        "bot.check_failed": "Не удалось проверить права бота.",
        "game.already": "В этом чате уже идёт набор или игра. /stop чтобы сбросить.",
        "game.none": "Активной игры нет.",
        "game.no_game": "Игры нет.",
        "game.stopped": "🛑 Игра остановлена.",
        "game.stop_denied": "Остановить может хост или админ чата.",
        "game.skip_nothing": "Нечего пропускать.",
        "game.skip_host": "Только хост может пропускать фазу.",
        "game.skip_denied_phase": "Эту фазу нельзя пропустить.",
        "players.status": "Фаза: <b>{phase}</b> | День {day}\nЖивые: {alive}\nМёртвые: {dead}",
        "phase.lobby": "набор",
        "phase.night": "ночь",
        "phase.day": "день",
        "phase.vote": "голосование",
        "phase.confirm": "подтверждение",
        "phase.kamikaze": "камикадзе",
        "phase.ended": "конец",
        "lobby.no_recruit": "Набора нет.",
        "lobby.already_in": "Вы уже в игре.",
        "lobby.no_slots": "Мест нет.",
        "lobby.joined": "Вы в игре!",
        "lobby.dm_joined": "Вы записались в Мафию в чате «{title}».\nДождитесь старта — роль придёт сюда.",
        "lobby.open_dm": "⚠️ {name}, откройте бота в личке и нажмите Start, иначе не получите роль.",
        "lobby.not_in": "Вас и так нет в списке.",
        "lobby.host_cant_leave": "Хост не может выйти. Отмените набор.",
        "lobby.left": "Вы вышли.",
        "lobby.nothing_cancel": "Нечего отменять.",
        "lobby.host_admin_only": "Только хост/админ.",
        "lobby.cancelled": "✖️ Набор отменён.",
        "lobby.host_start_only": "Только хост может начать.",
        "lobby.need_min": "Нужно минимум {n} игроков.",
        "lobby.starting": "Старт!",
        "bot.need_make_admin": (
            "🤵🏻 Мафия в чате.\n\n"
            "Сделайте @{username} <b>администратором</b> с правами:\n"
            "• удаление сообщений\n"
            "• ограничение участников\n\n"
            "После этого я подтвержу готовность."
        ),
        "bot.need_rights": (
            "⚠️ Я уже админ, но не хватает прав.\n\n"
            "Включите:\n"
            "• удаление сообщений\n"
            "• ограничение участников"
        ),
        "bot.ready": (
            "✅ Готово! Я администратор и могу вести игру.\n\n"
            "• /game — начать набор\n"
            "• игроки: /start боту в личке\n"
            "• владелец: /lang — язык чата"
        ),
        # game flow group
        "game.started": "🎭 Игра началась! Игроков: {n}\n\n{hint}",
        "game.roles_hint": (
            "Роли розданы в личные сообщения.\n"
            "Если бот не написал вам — откройте диалог с ботом и нажмите Start."
        ),
        "game.dm_failed": "\n\n⚠️ Не смог написать: {names}",
        "game.family": "Ваша семья:\n{list}",
        "btn.go_bot": "Перейти к боту",
        "btn.vote": "Голосовать",
        "night.city_sleeps": (
            "🌃 <b>Наступает ночь</b>\n"
            "На улицы города выходят лишь самые отважные и бесстрашные. "
            "Утром попробуем сосчитать их головы..."
        ),
        "night.wake.maniac": "<b>🔪 Маньяк</b> спрятался глубоко в кустах...",
        "night.wake.lawyer": "<b>👨🏼‍💼 Адвокат</b> ищет мафию для защиты...",
        "night.wake.doctor": "<b>👨🏼‍⚕️ Доктор</b> вышел на ночное дежурство...",
        "night.wake.commissioner": "<b>🕵️‍ Комиссар Каттани</b> ушёл искать злодеев...",
        "night.wake.mistress": "<b>💃🏼 Любовница</b> уже ждёт кого-то в гости...",
        "night.wake.mafia": "<b>🤵🏻 Мафия</b> выбрала жертву...",
        "night.wake.homeless": "<b>🧙‍♂️ Бомж</b> бродит по тёмным улицам...",
        "night.alive_header": "<b>Живые игроки:</b>",
        "night.sleep_left_1": "Спать осталось 1 мин.",
        "night.sleep_left_n": "Спать осталось {n} мин.",
        "day.sunrise": (
            "🏙 <b>День {n}</b>\n"
            "Солнце всходит, подсушивая на тротуарах пролитую ночью кровь..."
        ),
        "day.city_wakes": "☀️ <b>Город просыпается...</b>\n\n{events}",
        "day.start": (
            "☀️ <b>День {n}</b>\n\n"
            "Живые обсуждают ночь. Мёртвые молчат.\n"
            "⏱ Обсуждение: {seconds} сек.{blocked}\n\n"
            "Живые: {alive}"
        ),
        "day.discuss": (
            "{alive_block}\n\n"
            "<b>Кто-то из них:</b>\n"
            "{composition}\n"
            "Всего: {total} чел.\n\n"
            "Сейчас самое время обсудить результаты ночи, "
            "разобраться в причинах и следствиях...{blocked}"
        ),
        "day.alive_header": "<b>Живые игроки:</b>",
        "day.blocked": "\n💋 Под чарами любовницы (молчат и не голосуют): {names}",
        "vote.start": (
            "<b>Пришло время определить и наказать виноватых.</b>\n"
            "Голосование продлится {seconds} секунд"
        ),
        "vote.cast": "{voter} проголосовал за {target}",
        "vote.cast_skip": "{voter} воздержался",
        "vote.tie": "Голоса разделились / никто не выбран. Казнь отменяется.",
        "confirm.start": (
            "Вы точно хотите линчевать {name}?\n\n"
            "Голосование завершено"
        ),
        "confirm.results": (
            "<b>Результаты голосования:</b>\n"
            "{yes} 👍  |  {no} 👎\n\n"
            "Вешаем {name}! :)"
        ),
        "confirm.failed": (
            "<b>Результаты голосования:</b>\n"
            "{yes} 👍  |  {no} 👎\n\n"
            "Казнь не подтверждена."
        ),
        "kamikaze.announce": "💣 Камикадзе! {name} выбирает, кого утащить с собой...",
        "kamikaze.none": "💣 Камикадзе никого не выбрал.",
        "kamikaze.took": "💣 Вместе с камикадзе погиб(ла) {name} — {role}.",
        "game.over": "🏁 <b>Игра окончена!</b>\nПобеда: {winners}\n\n<b>Роли:</b>",
        "game.over.role_line": "{status} {name} — {role}",
        # night DM
        "night.blocked": "💋 Вы под действием любовницы и пропускаете ночь.",
        "night.mafia_pick": "😎 Ночь. Выберите жертву мафии:",
        "night.comm_mode": "🔍 Ночь комиссара. Что делаем?",
        "night.doctor_pick": "💊 Кого спасаем этой ночью?{extra}",
        "night.doctor_self_ok": " (самолечение ещё доступно)",
        "night.doctor_self_no": " (себя уже нельзя)",
        "night.maniac_pick": "🔪 Выберите жертву:",
        "night.mistress_pick": "💋 Кого отвлечь на ночь?",
        "night.lawyer_pick": "💼 Выберите подзащитного:",
        "night.homeless": "🚶 Вы бродите по городу. Утром узнаете, кого видели.",
        "night.sergeant": "👮 Вы дежурите. Если комиссар сделает проверку — я сообщу результат.",
        "btn.check": "🔍 Проверить",
        "btn.shoot": "🔫 Выстрелить",
        "btn.abstain": "⏭ Воздержаться",
        "btn.yes": "✅ За",
        "btn.no": "❌ Против",
        "vote.dm": "🗳 За кого ваш голос?",
        "vote.cant": "💋 Вы не можете голосовать сегодня.",
        "confirm.dm": "Подтвердить казнь {name}?",
        "kamikaze.dm": "💣 Выберите жертву:",
        # night resolve private / public (engine keys)
        "priv.mistress_block": "💋 Любовница отвлекла вас. Вы бездействуете этой ночью и весь следующий день.",
        "priv.mistress_ok": "Вы провели ночь с {name}.",
        "priv.lawyer_client": "Ваш подзащитный: {name}.",
        "priv.comm_check": "🔍 Проверка: {name} — {label}.",
        "priv.sergeant_check": "👮 Комиссар проверил {name}: {label}.",
        "priv.doctor_self_used": "Вы уже использовали самолечение. Лечение не сработало.",
        "priv.doctor_went": "Вы выехали к {name}.",
        "priv.homeless_seen": "🚶 Ночные наблюдения:\n{lines}",
        "priv.homeless_visit": "• Кто-то ({label}) ходил к {name}",
        "priv.homeless_quiet": "🚶 Ночь была тихой — вы никого не заметили.",
        "pub.saved": "💊 Доктор спас {name} этой ночью!",
        "pub.lucky": "🍀 На {name} было покушение, но удача на стороне счастливчика!",
        "pub.death": (
            "Сегодня был жестоко убит <b>{role}</b> {name}...\n"
            "Говорят, у него в гостях был {killer}"
        ),
        "pub.quiet": "Ночь прошла спокойно. Никто не погиб.",
        "pub.promote_comm": "👮 {name} повышен до Комиссара.",
        "pub.promote_don": "😎 {name} становится новым Доном.",
        "pub.lynch": "⚖️ Город казнил {name} — {role}.",
        "pub.lynch_reveal": "{name} был {role}",
        "pub.suicide_win": "💀 Самоубийца добился своей цели и побеждает!",
        "pub.already_dead": "Жертва уже мертва.",
        "win.draw": "Ничья — все мертвы",
        "win.maniac": "🔪 Маньяк",
        "win.mafia": "😎 Мафия",
        "win.town": "🏙️ Мирные жители",
        "win.suicide": "💀 Самоубийца",
        # actions callbacks
        "cb.not_now": "Сейчас нельзя.",
        "cb.not_yours": "Не ваше действие.",
        "cb.mistress": "Вас отвлекла любовница.",
        "cb.bad_target": "Недопустимая цель.",
        "cb.mafia_vote": "Голос учтён.",
        "cb.mafia_voted": "Вы голосуете за убийство: {name}",
        "cb.comm_whom_check": "🔍 Кого проверить?",
        "cb.comm_whom_shoot": "🔫 В кого выстрелить?",
        "cb.pick_action": "Сначала выберите действие.",
        "cb.accepted": "Принято.",
        "cb.comm_done": "Комиссар: {action} → {name}",
        "cb.comm_check_act": "проверка",
        "cb.comm_shoot_act": "выстрел",
        "cb.self_heal_used": "Самолечение уже использовано.",
        "cb.doctor_go": "Выезжаю!",
        "cb.doctor_done": "💊 Лечение: {name}",
        "cb.maniac_ok": "Жертва выбрана.",
        "cb.maniac_done": "🔪 Жертва: {name}",
        "cb.ok": "Ок.",
        "cb.mistress_done": "💋 Отвлекаете: {name}",
        "cb.lawyer_ok": "Клиент выбран.",
        "cb.lawyer_done": "💼 Подзащитный: {name}",
        "cb.not_in_game": "Вы не в игре.",
        "cb.cant_vote": "Сейчас нельзя голосовать.",
        "cb.abstained": "Воздержались.",
        "cb.you_abstained": "Вы воздержались.",
        "cb.bad_vote": "Недопустимый голос.",
        "cb.voted_for": "Голос за {name}",
        "cb.your_vote": "Ваш голос: {name}",
        "cb.cant_confirm": "Вы не голосуете сегодня.",
        "cb.yes": "За",
        "cb.no": "Против",
        "cb.kami_only": "Только камикадзе.",
        "cb.picked": "Выбрано.",
        "cb.kami_take": "Вы утаскиваете: {name}",
    },
    "uk": {
        "role.civilian.title": "Мирний житель",
        "role.civilian.desc": "Вночі спить. Вдень шукає мафію і голосує.",
        "role.don.title": "Дон",
        "role.don.desc": "Глава мафії. Вночі разом із сім'єю обирає жертву. Його голос вирішальний.",
        "role.mafia.title": "Мафія",
        "role.mafia.desc": "Член сім'ї. Вночі обирає жертву разом із Доном.",
        "role.commissioner.title": "Комісар",
        "role.commissioner.desc": "Вночі може перевірити роль гравця або вистрілити.",
        "role.sergeant.title": "Сержант",
        "role.sergeant.desc": "Дізнається про перевірки комісара. Після загибелі комісара стає ним.",
        "role.doctor.title": "Лікар",
        "role.doctor.desc": "Вночі рятує одного гравця. Себе — лише один раз за гру.",
        "role.maniac.title": "Маніяк",
        "role.maniac.desc": "Вбиває щоночі. Перемога — знищити всіх інших.",
        "role.mistress.title": "Коханка",
        "role.mistress.desc": "Відволікає гравця на ніч і наступний день.",
        "role.lawyer.title": "Адвокат",
        "role.lawyer.desc": "Обирає підзахисного. Перевірка комісара покаже «мирний».",
        "role.suicide.title": "Самогубець",
        "role.suicide.desc": "Перемагає лише якщо його стратять денним голосуванням.",
        "role.homeless.title": "Безхатько",
        "role.homeless.desc": "Бачить нічні візити: хто до кого ходив.",
        "role.lucky.title": "Щасливчик",
        "role.lucky.desc": "При замаху може вижити завдяки удачі.",
        "role.kamikaze.title": "Камікадзе",
        "role.kamikaze.desc": "При повішенні може забрати з собою одного гравця.",
        "role.card": "Ваша роль: {emoji} <b>{title}</b>\n\n{desc}",
        "role.civilian.short": "👤 Мирний житель",
        "visit.mistress": "Коханка",
        "visit.lawyer": "Адвокат",
        "visit.mafia": "Мафія",
        "visit.maniac": "Маніяк",
        "visit.commissioner": "Комісар",
        "visit.doctor": "Лікар",
        "start.welcome": (
            "🤵🏻 <b>Мафія</b>\n\n"
            "Безкоштовний бот для гри в Мафію в Telegram-чатах.\n\n"
            "Додайте мене до групи і зробіть адміністратором "
            "(видалення повідомлень + обмеження учасників), потім напишіть /game"
        ),
        "rules.text": (
            "🎭 <b>Мафія — правила</b>\n\n"
            "Гра в груповому чаті. Вночі тиша: дії в особистих з ботом.\n"
            "Вдень живі обговорюють і голосують, мертві мовчать.\n\n"
            "<b>Перемога</b>\n"
            "🏙️ Мирні — знищені мафія і маніяк\n"
            "😎 Мафія — мафіозі ≥ решти\n"
            "🔪 Маніяк — лишився один / убив усіх\n"
            "💀 Самогубець — страчений денним голосуванням\n\n"
            "Команди в чаті:\n"
            "/game — створити набір\n"
            "/stop — зупинити гру (хост/адмін)\n"
            "/players — список гравців\n"
            "/skip — достроково перейти до наступної фази (хост)\n"
            "/lang — мова чату (лише власник)"
        ),
        "btn.add_to_chat": "➕ Додати бота до чату",
        "btn.rules": "📖 Правила",
        "btn.lang": "🌐 Мова",
        "btn.lang_ru": "🇷🇺 Русский",
        "btn.lang_uk": "🇺🇦 Українська",
        "lang.choose_private": "Оберіть мову бота (особисті повідомлення):",
        "lang.choose_chat": "Оберіть мову чату (повідомлення в групі):",
        "lang.set_private": "✅ Мова бота: {lang_name}",
        "lang.set_chat": "✅ Мова чату: {lang_name}",
        "lang.name.ru": "Русский",
        "lang.name.uk": "Українська",
        "lang.only_owner": "Мову чату може змінювати лише власник групи.",
        "lang.current_private": "Ваша мова в боті: <b>{lang_name}</b>",
        "lang.current_chat": "Мова цього чату: <b>{lang_name}</b>",
        "btn.join": "✅ Приєднатися",
        "btn.leave": "🚪 Вийти",
        "btn.start_game": "▶️ Почати гру",
        "btn.cancel": "✖️ Скасувати",
        "lobby.title": "🎭 <b>Набір у Мафію</b>",
        "lobby.players": "Гравці ({n}):",
        "lobby.empty": "— поки нікого —",
        "lobby.hint": "Хост: натисніть «Почати гру», коли всі готові.",
        "lobby.need": "Потрібно від {min} до {max} гравців.",
        "bot.need_admin": (
            "Зробіть бота адміністратором чату з правами:\n"
            "• видалення повідомлень\n"
            "• обмеження учасників"
        ),
        "bot.check_failed": "Не вдалося перевірити права бота.",
        "game.already": "У цьому чаті вже йде набір або гра. /stop щоб скинути.",
        "game.none": "Активної гри немає.",
        "game.no_game": "Гри немає.",
        "game.stopped": "🛑 Гру зупинено.",
        "game.stop_denied": "Зупинити може хост або адмін чату.",
        "game.skip_nothing": "Нічого пропускати.",
        "game.skip_host": "Лише хост може пропускати фазу.",
        "game.skip_denied_phase": "Цю фазу не можна пропустити.",
        "players.status": "Фаза: <b>{phase}</b> | День {day}\nЖиві: {alive}\nМертві: {dead}",
        "phase.lobby": "набір",
        "phase.night": "ніч",
        "phase.day": "день",
        "phase.vote": "голосування",
        "phase.confirm": "підтвердження",
        "phase.kamikaze": "камікадзе",
        "phase.ended": "кінець",
        "lobby.no_recruit": "Набору немає.",
        "lobby.already_in": "Ви вже в грі.",
        "lobby.no_slots": "Місць немає.",
        "lobby.joined": "Ви в грі!",
        "lobby.dm_joined": "Ви записалися в Мафію в чаті «{title}».\nДочекайтеся старту — роль прийде сюди.",
        "lobby.open_dm": "⚠️ {name}, відкрийте бота в особистих і натисніть Start, інакше не отримаєте роль.",
        "lobby.not_in": "Вас і так немає в списку.",
        "lobby.host_cant_leave": "Хост не може вийти. Скасуйте набір.",
        "lobby.left": "Ви вийшли.",
        "lobby.nothing_cancel": "Нічого скасовувати.",
        "lobby.host_admin_only": "Лише хост/адмін.",
        "lobby.cancelled": "✖️ Набір скасовано.",
        "lobby.host_start_only": "Лише хост може почати.",
        "lobby.need_min": "Потрібно мінімум {n} гравців.",
        "lobby.starting": "Старт!",
        "bot.need_make_admin": (
            "🤵🏻 Мафія в чаті.\n\n"
            "Зробіть @{username} <b>адміністратором</b> з правами:\n"
            "• видалення повідомлень\n"
            "• обмеження учасників\n\n"
            "Після цього я підтверджу готовність."
        ),
        "bot.need_rights": (
            "⚠️ Я вже адмін, але не вистачає прав.\n\n"
            "Увімкніть:\n"
            "• видалення повідомлень\n"
            "• обмеження учасників"
        ),
        "bot.ready": (
            "✅ Готово! Я адміністратор і можу вести гру.\n\n"
            "• /game — почати набір\n"
            "• гравці: /start боту в особистих\n"
            "• власник: /lang — мова чату"
        ),
        "game.started": "🎭 Гру розпочато! Гравців: {n}\n\n{hint}",
        "game.roles_hint": (
            "Ролі роздано в особисті повідомлення.\n"
            "Якщо бот не написав вам — відкрийте діалог із ботом і натисніть Start."
        ),
        "game.dm_failed": "\n\n⚠️ Не зміг написати: {names}",
        "game.family": "Ваша сім'я:\n{list}",
        "btn.go_bot": "Перейти до бота",
        "btn.vote": "Голосувати",
        "night.city_sleeps": (
            "🌃 <b>Настає ніч</b>\n"
            "На вулиці міста виходять лише найвідважніші і безстрашні. "
            "Вранці спробуємо порахувати їхні голови..."
        ),
        "night.wake.maniac": "<b>🔪 Маніяк</b> сховався глибоко в кущах...",
        "night.wake.lawyer": "<b>👨🏼‍💼 Адвокат</b> шукає мафію для захисту...",
        "night.wake.doctor": "<b>👨🏼‍⚕️ Лікар</b> вийшов на нічне чергування...",
        "night.wake.commissioner": "<b>🕵️‍ Комісар Каттані</b> пішов шукати лиходіїв...",
        "night.wake.mistress": "<b>💃🏼 Коханка</b> вже чекає когось у гості...",
        "night.wake.mafia": "<b>🤵🏻 Мафія</b> обрала жертву...",
        "night.wake.homeless": "<b>🧙‍♂️ Безхатько</b> блукає темними вулицями...",
        "night.alive_header": "<b>Живі гравці:</b>",
        "night.sleep_left_1": "Спати залишилось 1 хв.",
        "night.sleep_left_n": "Спати залишилось {n} хв.",
        "day.sunrise": (
            "🏙 <b>День {n}</b>\n"
            "Сонце сходить, підсушуючи на тротуарах пролиту вночі кров..."
        ),
        "day.city_wakes": "☀️ <b>Місто прокидається...</b>\n\n{events}",
        "day.start": (
            "☀️ <b>День {n}</b>\n\n"
            "Живі обговорюють ніч. Мертві мовчать.\n"
            "⏱ Обговорення: {seconds} сек.{blocked}\n\n"
            "Живі: {alive}"
        ),
        "day.discuss": (
            "{alive_block}\n\n"
            "<b>Хтось із них:</b>\n"
            "{composition}\n"
            "Всього: {total} осіб.\n\n"
            "Зараз саме час обговорити результати ночі, "
            "розібратися в причинах і наслідках...{blocked}"
        ),
        "day.alive_header": "<b>Живі гравці:</b>",
        "day.blocked": "\n💋 Під чарами коханки (мовчать і не голосують): {names}",
        "vote.start": (
            "<b>Прийшов час визначити і покарати винних.</b>\n"
            "Голосування триватиме {seconds} секунд"
        ),
        "vote.cast": "{voter} проголосував за {target}",
        "vote.cast_skip": "{voter} утримався",
        "vote.tie": "Голоси розділилися / нікого не обрано. Страту скасовано.",
        "confirm.start": (
            "Ви точно хочете лінчувати {name}?\n\n"
            "Голосування завершено"
        ),
        "confirm.results": (
            "<b>Результати голосування:</b>\n"
            "{yes} 👍  |  {no} 👎\n\n"
            "Вішаємо {name}! :)"
        ),
        "confirm.failed": (
            "<b>Результати голосування:</b>\n"
            "{yes} 👍  |  {no} 👎\n\n"
            "Страту не підтверджено."
        ),
        "kamikaze.announce": "💣 Камікадзе! {name} обирає, кого забрати з собою...",
        "kamikaze.none": "💣 Камікадзе нікого не обрав.",
        "kamikaze.took": "💣 Разом із камікадзе загинув(ла) {name} — {role}.",
        "game.over": "🏁 <b>Гру закінчено!</b>\nПеремога: {winners}\n\n<b>Ролі:</b>",
        "game.over.role_line": "{status} {name} — {role}",
        "night.blocked": "💋 Ви під дією коханки і пропускаєте ніч.",
        "night.mafia_pick": "😎 Ніч. Оберіть жертву мафії:",
        "night.comm_mode": "🔍 Ніч комісара. Що робимо?",
        "night.doctor_pick": "💊 Кого рятуємо цієї ночі?{extra}",
        "night.doctor_self_ok": " (самолікування ще доступне)",
        "night.doctor_self_no": " (себе вже не можна)",
        "night.maniac_pick": "🔪 Оберіть жертву:",
        "night.mistress_pick": "💋 Кого відволікти на ніч?",
        "night.lawyer_pick": "💼 Оберіть підзахисного:",
        "night.homeless": "🚶 Ви блукаєте містом. Вранці дізнаєтесь, кого бачили.",
        "night.sergeant": "👮 Ви чергуєте. Якщо комісар зробить перевірку — я повідомлю результат.",
        "btn.check": "🔍 Перевірити",
        "btn.shoot": "🔫 Вистрілити",
        "btn.abstain": "⏭ Утриматися",
        "btn.yes": "✅ За",
        "btn.no": "❌ Проти",
        "vote.dm": "🗳 За кого ваш голос?",
        "vote.cant": "💋 Ви не можете голосувати сьогодні.",
        "confirm.dm": "Підтвердити страту {name}?",
        "kamikaze.dm": "💣 Оберіть жертву:",
        "priv.mistress_block": "💋 Коханка відволікла вас. Ви бездієте цієї ночі і весь наступний день.",
        "priv.mistress_ok": "Ви провели ніч із {name}.",
        "priv.lawyer_client": "Ваш підзахисний: {name}.",
        "priv.comm_check": "🔍 Перевірка: {name} — {label}.",
        "priv.sergeant_check": "👮 Комісар перевірив {name}: {label}.",
        "priv.doctor_self_used": "Ви вже використали самолікування. Лікування не спрацювало.",
        "priv.doctor_went": "Ви виїхали до {name}.",
        "priv.homeless_seen": "🚶 Нічні спостереження:\n{lines}",
        "priv.homeless_visit": "• Хтось ({label}) ходив до {name}",
        "priv.homeless_quiet": "🚶 Ніч була тихою — ви нікого не помітили.",
        "pub.saved": "💊 Лікар врятував {name} цієї ночі!",
        "pub.lucky": "🍀 На {name} був замах, але удача на боці щасливчика!",
        "pub.death": (
            "Сьогодні жорстоко вбито <b>{role}</b> {name}...\n"
            "Кажуть, у нього в гостях був {killer}"
        ),
        "pub.quiet": "Ніч минула спокійно. Ніхто не загинув.",
        "pub.promote_comm": "👮 {name} підвищений до Комісара.",
        "pub.promote_don": "😎 {name} стає новим Доном.",
        "pub.lynch": "⚖️ Місто стратило {name} — {role}.",
        "pub.lynch_reveal": "{name} був {role}",
        "pub.suicide_win": "💀 Самогубець досяг своєї мети і перемагає!",
        "pub.already_dead": "Жертва вже мертва.",
        "win.draw": "Нічия — усі мертві",
        "win.maniac": "🔪 Маніяк",
        "win.mafia": "😎 Мафія",
        "win.town": "🏙️ Мирні жителі",
        "win.suicide": "💀 Самогубець",
        "cb.not_now": "Зараз не можна.",
        "cb.not_yours": "Не ваша дія.",
        "cb.mistress": "Вас відволікла коханка.",
        "cb.bad_target": "Неприпустима ціль.",
        "cb.mafia_vote": "Голос враховано.",
        "cb.mafia_voted": "Ви голосуєте за вбивство: {name}",
        "cb.comm_whom_check": "🔍 Кого перевірити?",
        "cb.comm_whom_shoot": "🔫 У кого вистрілити?",
        "cb.pick_action": "Спочатку оберіть дію.",
        "cb.accepted": "Прийнято.",
        "cb.comm_done": "Комісар: {action} → {name}",
        "cb.comm_check_act": "перевірка",
        "cb.comm_shoot_act": "постріл",
        "cb.self_heal_used": "Самолікування вже використано.",
        "cb.doctor_go": "Виїжджаю!",
        "cb.doctor_done": "💊 Лікування: {name}",
        "cb.maniac_ok": "Жертву обрано.",
        "cb.maniac_done": "🔪 Жертва: {name}",
        "cb.ok": "Ок.",
        "cb.mistress_done": "💋 Відволікаєте: {name}",
        "cb.lawyer_ok": "Клієнта обрано.",
        "cb.lawyer_done": "💼 Підзахисний: {name}",
        "cb.not_in_game": "Ви не в грі.",
        "cb.cant_vote": "Зараз не можна голосувати.",
        "cb.abstained": "Утрималися.",
        "cb.you_abstained": "Ви утрималися.",
        "cb.bad_vote": "Неприпустимий голос.",
        "cb.voted_for": "Голос за {name}",
        "cb.your_vote": "Ваш голос: {name}",
        "cb.cant_confirm": "Ви не голосуєте сьогодні.",
        "cb.yes": "За",
        "cb.no": "Проти",
        "cb.kami_only": "Лише камікадзе.",
        "cb.picked": "Обрано.",
        "cb.kami_take": "Ви забираєте: {name}",
    },
}
