import json

with open("i18n/ru.json", "r", encoding="utf-8") as f:
    ru = json.load(f)

# Исправления
fixes = {
    "RIDERS WERE HOSTILE--CHECK FOR LOSSES": "ВСАДНИКИ БЫЛИ ВРАЖДЕБНЫ--ПРОВЕРЬТЕ ПОТЕРИ",
    "YOU'D BETTER DO SOME HUNTING OR BUY FOOD AND SOON!!!!": "ВАМ ЛУЧШЕ ПОЙТИ НА ОХОТУ ИЛИ КУПИТЬ ЕДУ, И ПОСКОРЕЕ!!!!!",
    "WAGON GETS SWAMPED FORDING RIVER--LOSE FOOD AND CLOTHES": "ФУРГОН ЗАЧЕРПНУЛ ВОДУ ПРИ ПЕРЕПРАВЕ--ПОТЕРЯ ЕДЫ И ОДЕЖДЫ",
    "YOUR SON GETS LOST---SPEND HALF THE DAY LOOKING FOR HIM": "ВАШ СЫН ЗАБЛУДИЛСЯ--ПОТРАТИТЕ ПОЛОВИНУ ДНЯ НА ЕГО ПОИСК",
    "OX WANDERS OFF--SPEND TIME LOOKING FOR IT": "ВОЛ ОТОШЁЛ--ПОТРАТИТЕ ВРЕМЯ НА ЕГО ПОИСК",
    "YOU HAD TO STOP AND USE SUPPLIES TO MAKE A SLING": "ВАМ ПРИШЛОСЬ ОСТАНОВИТЬСЯ И ИСПОЛЬЗОВАТЬ ЗАПАСЫ, ЧТОБЫ СДЕЛАТЬ ПРАЩУ",
    "RUGGED MOUNTAINS": "СКАЛИСТЫЕ ГОРЫ",
    "THE GOING GETS SLOW": "ДВИЖЕНИЕ ЗАМЕДЛЯЕТСЯ",
    "YOU GOT LOST---LOSE VALUABLE TIME TRYING TO FIND TRAIL!": "ВЫ ЗАБЛУДИЛИСЬ--ПОТЕРЯ ЦЕННОГО ВРЕМЕНИ ПРИ ПОИСКЕ ТРОПЫ!",
    "YOU DIED OF PNEUMONIA": "ВЫ УМЕРЛИ ОТ ПНЕВМОНИИ",
    "AND WISHES YOU A PROSPEROUS LIFE AHEAD": "И ЖЕЛАЕТ ВАМ ПРОЦВЕТАНИЯ В БУДУЩЕЙ ЖИЗНИ",
    "YOU FINALLY ARRIVED AT OREGON CITY": "ВЫ НАКОНЕЦ ДОБРАЛИСЬ ДО ОРЕГОН-СИТИ",
    "BAD ILLNESS---MEDICINE USED": "ТЯЖЁЛАЯ БОЛЕЗНЬ--ИСПОЛЬЗОВАНО ЛЕКАРСТВО",
    "MILD ILLNESS---MEDICINE USED": "ЛЁГКАЯ БОЛЕЗНЬ--ИСПОЛЬЗОВАНО ЛЕКАРСТВО",
    "CASH : $": "НАЛИЧНЫЕ: $",
    "MISC. SUPPLIES: ": "ПРОЧИЕ ЗАПАСЫ: ",
    "TOUGH---YOU NEED M0RE BULLETS TO GO HUNTING": "ПЛОХО--ВАМ НУЖНО БОЛЬШЕ ПАТРОНОВ ДЛЯ ОХОТЫ",
    "ENTER WHAT YOU WISH TO SPEND ON THE FOLLOWING: ": "ВВЕДИТЕ СУММУ, КОТОРУЮ ХОТИТЕ ПОТРАТИТЬ НА СЛЕДУЮЩЕЕ: ",
    "YOU DON'T HAVE THAT MUCH--KEEP YOUR SPENDING DOWN": "У ВАС НЕТ СТОЛЬКО--УМЕРЬТЕ АППЕТИТЫ",
    "YOU HAVE TO SEE OL' DOC BLANCHARD": "ВАМ НУЖНО ОБРАТИТЬСЯ К СТАРОМУ ДОКУ БЛАНШАРДУ",
    "KINDA SLOW WITH YOUR COLT .45": "НЕМЕДЛИТЕЛЬНО С ВАШИМ КОЛЬТОМ .45",
    "THE WOLVES OVERPOWERED YOU": "ВОЛКИ ОДОЛЕЛИ ВАС",
    "LOSE YOUR WAY IN HEAVY FOG---TIME IS LOST": "ЗАБЛУДИЛИСЬ В ГУСТОМ ТУМАНЕ--ВРЕМЯ ПОТЕРЯНО",
    "THERE WAS A FIRE IN YOUR WAGON--FOOD AND SUPPLIES DAMAGE!": "В ФУРГОНЕ ПРОИЗОШЁЛ ПОЖАР--ПОВРЕЖДЕНА ЕДА И ЗАПАСЫ!",
    "HELPFUL INDIANS SHOW YOU WERE TO FIND MORE FOOD": "ДОБРОЖЕЛАТЕЛЬНЫЕ ИНДЕЙЦЫ ПОКАЗАЛИ ВАМ, ГДЕ НАЙТИ БОЛЬШЕ ЕДЫ",
    "BETTER HAVE A DOC LOOK AT YOUR WOUND": "ЛУЧШЕ ПОКАЖИТЕ РАНУ ВРАЧУ",
    "YOU GOT SHOT IN THE LEG AND THEY TOOK ONE OF YOUR OXEN": "ВАМ ПРОСТРЕЛИЛИ НОГУ, И ОНИ ЗАБРАЛИ ОДНОГО ИЗ ВАШИХ ВОЛОВ",
}

# Удаляем проблемную строку с переменной
key_to_remove = "AFTER g_vars.GOAL_IN_MILES LONG MILES---HOORAY !!!!!"
if key_to_remove in ru:
    del ru[key_to_remove]
    print(f"Удалена строка с переменной: {key_to_remove}")

# Применяем исправления
for key, new_value in fixes.items():
    if key in ru:
        ru[key] = new_value
        print(f"Исправлено: {key[:50]}...")

# Приводим к единому регистру (ALL CAPS для всех сообщений)
for key in ru:
    if key.isupper() or key.startswith("="):
        # Если ключ в ALL CAPS, значение тоже должно быть
        if not ru[key].isupper() and not ru[key].startswith("="):
            ru[key] = ru[key].upper()

with open("i18n/ru.json", "w", encoding="utf-8") as f:
    json.dump(ru, f, ensure_ascii=False, indent=2)

print(f"\nИсправлено {len(fixes)} строк")
print("Файл сохранён")
