from typing import Any, cast
import flet as ft
from audiofix import Audio

import question as q
import random

def main(page: ft.Page) -> None:
    all_wqs = q.load_questions()
    wqs : list[q.WordQuestion] = []
    queue : list[q.WordQuestion] = []
    stats = q.load_stats()
    rng = random.Random()
    selected_wq : q.WordQuestion

    def requeue() -> None:
        nonlocal queue
        def is_never_tried(wq : q.WordQuestion) -> bool:
            if wq.word.no not in stats.stats:
                return True
            return stats.stats[wq.word.no].total == 0
        never_tried : list[q.WordQuestion] = [ wq for wq in wqs if is_never_tried(wq) ]
        if never_tried != []:
            queue = never_tried[:10]
            print('never tried:', len(queue), '/', len(never_tried))
        else:
            wqs_ratio = []
            for wq in wqs:
                stat = stats.stats[wq.word.no]
                wqs_ratio.append((wq, float(stat.failures + 5) / float(stat.total * stat.total)))
            rng.shuffle(wqs_ratio)
            wqs_ratio.sort(key=lambda x:x[1], reverse=True)
            queue = [wq for (wq, _) in wqs_ratio[:int(len(wqs_ratio)/3)+1]]
            failures = [stats.stats[wq.word.no].failures for wq in queue]
            print('retry:', failures)
        rng.shuffle(queue)

    audio1 = Audio(src="audio/「さあ、いくぞ！」.mp3")
    audio_correct = Audio(src="audio/クイズ正解2.mp3")
    audio_wrong = Audio(src="audio/クイズ不正解1.mp3")
    page.overlay.append(audio1)
    page.overlay.append(audio_correct)
    page.overlay.append(audio_wrong)

    def centered(x : ft.Control) -> ft.Container:
        return ft.Container(                            
            x,
            alignment=ft.alignment.center,
        )

    number_text = ft.Text('番号', size=20)
    question_text = ft.Text('問題', size=30)
    japanese_text = ft.Text('和訳', size=30)
    result_text = ft.Text('結果', size=50)

    result = ft.Container(
        result_text,
        alignment=ft.alignment.center,
        visible= False
    )

    answer_but = ft.OutlinedButton(
        '回答',
        style= ft.ButtonStyle(
            text_style=ft.TextStyle(size=40),
            shape= ft.RoundedRectangleBorder(radius=10),
            padding=15,
        ),
    )

    answer = ft.Container(
        answer_but,
        alignment=ft.alignment.center,
        visible= False
    )
    
    def make_button(s: str) -> ft.OutlinedButton:
        return ft.OutlinedButton(
            s, 
            style= ft.ButtonStyle(
                text_style=ft.TextStyle(size=30),
                shape= ft.RoundedRectangleBorder(radius=10),
                padding=15,
            ),
        )

    buttons : list[ft.OutlinedButton] = [ make_button(str(i)) for i in range(0,6) ]

    playarea = ft.Column(
        [
            centered(number_text),
            centered(question_text),
            centered(japanese_text),
            centered(ft.Row( 
                buttons,
                wrap= True,
                alignment= ft.MainAxisAlignment.CENTER,
            )),
            result,
            answer,
        ],
        alignment= ft.MainAxisAlignment.SPACE_EVENLY,
        # expand= True,
        visible= False,
    )

    mode_select : ft.Column

    def select_mode(mod : int, e : ft.ControlEvent) -> None:
        playarea.visible = True
        mode_select.visible = False
        nonlocal wqs
        if mod == -1:
            wqs = all_wqs
        else:
            wqs = [wq for wq in all_wqs if wq.word.no % 8 == mod]
        load_next()
        audio1.play()
        page.update()

    import functools

    def mode_button(mod : int, label : str|None=None) -> ft.OutlinedButton:
        return ft.OutlinedButton(
            text= label if label is not None else f'{mod}',
            style= ft.ButtonStyle(
                text_style=ft.TextStyle(size=30),
                shape= ft.RoundedRectangleBorder(radius=10),
                padding=15,
            ),
            on_click= functools.partial(select_mode, mod)
        )

    mode_select = ft.Column(
        [
            centered(ft.Text('モードセレクト', size=30)),
            centered(ft.Row(
                [
                    mode_button(0),
                    mode_button(1),
                    mode_button(2),
                    mode_button(3),
                    mode_button(4),
                    mode_button(5),
                    mode_button(6),
                    mode_button(7),
                    mode_button(-1,'全部'),
                ],
                wrap=True,
            ))
        ],
        # alignment= ft.MainAxisAlignment.SPACE_EVENLY,
        # expand= True,
    )

    page.add(
        ft.SafeArea(
            ft.Column(
                [
                    ft.Container(
                        ft.Text('X高春単語マスター', size=50),
                        alignment=ft.alignment.center,
                    ),
                    mode_select,
                    playarea,
                ],
            ),
            # expand=True,
        )
    )

    def make_puzzle(wq : q.WordQuestion) -> None:
        options = q.make_options(rng, wq, 6)
        for (b,o) in zip (buttons, options):
            b.text = o

    def load_puzzle(new_wq : q.WordQuestion) -> None:
        nonlocal selected_wq
        selected_wq = new_wq
        number_text.value = str(selected_wq.word.no)
        question_text.value = selected_wq.question.question
        japanese_text.value = selected_wq.word.japanese
        answer_but.text = f'{selected_wq.word.word} : {selected_wq.word.meaning} ({selected_wq.word.klass})'
        make_puzzle(selected_wq)
        page.update()

    def load_next() -> None:
        nonlocal queue
        if queue == []:
            q.save_stats(stats)
            requeue()
        wq = queue[0]
        queue = queue[1:]
        load_puzzle(wq)

    def clicked(e : ft.ControlEvent) -> None:
        correct = e.control.text == selected_wq.question.answer 
        if correct:
            audio_correct.play()
        else:
            audio_wrong.play()

        stat : q.Stat = stats.stats.get(
            selected_wq.word.no,
            q.Stat(total=0, failures=0)
        )
        stat.total += 1
        if not correct:
            stat.failures += 1
        stats.stats[selected_wq.word.no] = stat

        result_text.value = '🎉 正解 🎉' if correct else '☹️ 不正解 ☹️'
        result.visible = True
        answer.visible = True
        for b in buttons:
            assert b.style is not None
            b.style.bgcolor = 'blue' if b.text == selected_wq.question.answer else 'red'
            b.style.color = 'white'
            b.disabled = True
        question_text.value = selected_wq.word.example
        page.update()

    def clicked2(e : ft.ControlEvent) -> None:
        for b in buttons:
            assert b.style is not None
            b.style.bgcolor = None
            b.style.color = None
            b.disabled = False
        result.visible = False
        answer.visible = False
        new_wq = rng.choice(wqs)
        load_next()
        page.update()

    for b in buttons:
        b.on_click = clicked

    answer_but.on_click = clicked2
    
ft.app(main)
