import streamlit as st
import random
import operator
import time

# --- 関数部分（変更なし） ---
def generate_question():
    """
    四則演算の問題と答えをランダムに生成する関数。
    割り算は必ず割り切れる数値を生成します。
    """
    ops = {
        '+': operator.add,
        '-': operator.sub,
        '×': operator.mul,
        '÷': operator.truediv
    }
    op_symbol = random.choice(list(ops.keys()))
    
    if op_symbol == '÷':
        divisor = random.randint(2, 10)
        dividend = divisor * random.randint(2, 10)
        num1 = dividend
        num2 = divisor
    elif op_symbol == '×':
        num1 = random.randint(2, 12)
        num2 = random.randint(2, 12)
    else:
        num1 = random.randint(1, 100)
        num2 = random.randint(1, 100)
        if op_symbol == '-' and num1 < num2:
            num1, num2 = num2, num1

    question = f"{num1} {op_symbol} {num2}"
    answer = ops[op_symbol](num1, num2)
    
    if op_symbol == '÷':
        answer = int(answer)

    return question, answer

# --- ここからが変更・追加部分 ---

def initialize_quiz_state(): 
    """クイズの状態を初期化（またはリセット）する関数"""
    q, a = generate_question()
    st.session_state.question = q
    st.session_state.answer = a
    st.session_state.score = 0
    st.session_state.total_questions = 0
    st.session_state.start_time = time.time() # 各問題の開始時間を記録
    st.session_state.feedback_message = "" # フィードバックメッセージ用
    st.session_state.feedback_type = "" # 'success', 'error', 'info', 'warning'
    st.session_state.quiz_history = [] # 回答履歴を保存するリストを初期化

def display_feedback():
    """フィードバックメッセージを表示するヘルパー関数"""
    if st.session_state.feedback_message:
        if st.session_state.feedback_type == "success":
            st.success(st.session_state.feedback_message)
        elif st.session_state.feedback_type == "error":
            st.error(st.session_state.feedback_message)
        elif st.session_state.feedback_type == "warning":
            st.warning(st.session_state.feedback_message)
        else:
            st.info(st.session_state.feedback_message)
        # メッセージを表示したらクリアする (ただし、これは次の問題表示時にクリアされる)
        # st.session_state.feedback_message = "" 
        # st.session_state.feedback_type = ""

def advance_question(message_type, message_text, user_ans, is_correct_flag, timed_out_flag=False):
    """次の問題に進むための共通処理"""
    # 現在の問題の情報を履歴に追加
    st.session_state.quiz_history.append({
        "question": st.session_state.question,
        "correct_answer": st.session_state.answer,
        "user_answer": user_ans,
        "is_correct": is_correct_flag,
        "timed_out": timed_out_flag
    })

    st.session_state.total_questions += 1
    st.session_state.feedback_type = message_type
    st.session_state.feedback_message = message_text
    
    # クイズが終了していなければ次の問題を生成
    if st.session_state.total_questions < 10:
        q, a = generate_question()
        st.session_state.question = q
        st.session_state.answer = a
        st.session_state.start_time = time.time() # 新しい問題の開始時間を記録
    
    # 画面を更新して新しい問題または終了画面を表示
    st.rerun()
    st.stop()


def main():
    """
    メインのアプリケーション部分
    """
    st.title("🔢 10問限定！四則演算クイズ")

    # セッションが初期化されていなければ、必要なキーを全て初期化する
    if 'question' not in st.session_state:
        initialize_quiz_state() 

    # --- 10問終了後の結果表示画面 ---
    if st.session_state.total_questions >= 10:
        st.header("クイズ終了！")
        
        # 最終スコアを大きく表示
        st.metric("最終スコア", f"{st.session_state.score} / 10")
        
        # スコアに応じたメッセージ
        if st.session_state.score == 10:
            st.success("🎉 全問正解！素晴らしい！ 🎉")
            st.balloons()
        elif st.session_state.score >= 7:
            st.info(f"おめでとうございます！なかなかの高得点です！")
        else:
            st.info(f"お疲れ様でした！また挑戦してみてくださいね。")
        
        # リセットボタン
        if st.button("もう一度挑戦する"):
            # initialize_quiz_stateを呼び出して、クイズの状態を完全にリセット
            initialize_quiz_state() 
            st.rerun() # 状態がリセットされた後に再描画
            st.stop() # 再描画を待たずに現在の実行を停止

        # --- 回答履歴の表示 ---
        # initialize_quiz_state() で quiz_history がクリアされるため、
        # 「もう一度挑戦する」クリック後はこのブロックは表示されなくなるか、
        # 「まだクイズの履歴はありません。」と表示されます。
        st.write("---")
        st.subheader("💡 クイズの振り返り")
        if st.session_state.quiz_history: # 履歴が存在する場合のみ表示
            for i, record in enumerate(st.session_state.quiz_history):
                status_icon = "✅" if record["is_correct"] else ("⏰" if record["timed_out"] else "❌")
                st.markdown(f"**{i+1}. 問題: {record['question']}** {status_icon}")
                st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;正解: **{record['correct_answer']}**")
                
                if not record["is_correct"]: # 不正解または時間切れの場合のみユーザーの回答を表示
                    user_ans_display = record["user_answer"] if record["user_answer"] is not None else "未回答"
                    st.write(f"&nbsp;&nbsp;&nbsp;&nbsp;あなたの回答: **{user_ans_display}**")
                st.write("---")
        else:
            st.info("まだクイズの履歴はありません。")


    # --- クイズ中の画面 (10問未満の場合) ---
    else:
        # 現在の問題番号を表示
        st.subheader(f"第 {st.session_state.total_questions + 1} 問")

        time_limit = 10 # 10秒の制限時間
        elapsed_time = time.time() - st.session_state.start_time

        # 時間切れチェック
        if elapsed_time >= time_limit:
            # 時間切れメッセージを表示し、次の問題へ進む
            advance_question("error", f"時間切れ！ 正しい答えは **{st.session_state.answer}** でした。",
                             user_ans=None, is_correct_flag=False, timed_out_flag=True)
            # advance_question内でst.rerun()とst.stop()が呼ばれるので、これ以上は不要

        # 残り時間を表示
        remaining_time = max(0, int(time_limit - elapsed_time))
        st.write(f"残り時間: **{remaining_time}** 秒")

        # スコア表示
        st.metric(label="現在のスコア", value=f"{st.session_state.score} / {st.session_state.total_questions}")
        st.divider()

        # 問題表示
        st.header(f"問題: {st.session_state.question} = ?")

        # フィードバックメッセージを表示（前回のrerunで設定されたもの）
        display_feedback() 

        # 回答フォーム
        with st.form(key='answer_form', clear_on_submit=True):
            user_answer = st.number_input("答えを入力してください:", value=None, format="%d", placeholder="半角数字で入力")
            submit_button = st.form_submit_button(label='回答する')

        # 回答処理
        if submit_button:
            if user_answer is not None:
                if int(user_answer) == st.session_state.answer:
                    st.session_state.score += 1
                    advance_question("success", "正解です！🎉", user_ans=int(user_answer), is_correct_flag=True)
                else:
                    advance_question("error", f"不正解... 正しい答えは **{st.session_state.answer}** でした。",
                                     user_ans=int(user_answer), is_correct_flag=False)
            else:
                advance_question("error", f"答えを入力してください。正しい答えは **{st.session_state.answer}** でした。",
                                 user_ans=None, is_correct_flag=False)
            # advance_question内でst.rerun()とst.stop()が呼ばれるので、これ以上は不要

        # Streamlitが定期的に再実行されるようにする（時間制限のチェックのため）
        # ユーザーが何も操作しない限り時間が経過しても画面が更新されないため
        time.sleep(0.1) 
        st.rerun()
        st.stop() 

if __name__ == '__main__':
    main()
