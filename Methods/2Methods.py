import csv
from datetime import datetime
from django.db import transaction
from django.http import HttpResponse
from ..Models.secModels import PlayerLevel, LevelPrize, Prize



def assign_prize_to_player(player_id, level_id):
    """Присвоение приза игроку за прохождение уровня"""
    try:
        with transaction.atomic():
            player_level = PlayerLevel.objects.select_for_update().get(
                player_id=player_id,
                level_id=level_id,
                is_completed=True
            )

            # Проверяем, не был ли приз уже получен
            if not LevelPrize.objects.filter(
                    level_id=level_id,
                    prize__playerlevel=player_level
            ).exists():
                prize = Prize.objects.create(title=f'Приз за уровень {player_level}')  # Создаем приз
                LevelPrize.objects.create(
                    level_id=level_id,
                    prize=prize,
                    received=datetime.now()
                )

    except PlayerLevel.DoesNotExist:
        raise ValueError("Уровень не пройден или не существует")


def export_player_levels_to_csv():
    """Выгрузка данных игроков в CSV"""
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="player_levels.csv"'

    writer = csv.writer(response)
    writer.writerow(['Player ID', 'Level Title', 'Completed', 'Prize Title'])

    # Оптимизация запросов для больших данных
    player_levels = PlayerLevel.objects.select_related(
        'level', 'player'
    ).prefetch_related(
        'level__levelprize_set__prize'
    ).all()

    for pl in player_levels.iterator(chunk_size=1000):  # Итерация по частям
        prize_title = ""
        if pl.is_completed:
            # Получаем первый приз уровня (если есть)
            level_prize = pl.level.levelprize_set.first()
            if level_prize:
                prize_title = level_prize.prize.title

        writer.writerow([
            pl.player.player_id,
            pl.level.title,
            'Yes' if pl.is_completed else 'No',
            prize_title
        ])

    return response