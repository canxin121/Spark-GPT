import asyncio
import json
import re
from playwright.async_api import ElementHandle
from playwright.sync_api import Page
from .config import poe_persistor
from nonebot import logger

async def send_message_async(page: Page, botname: str, input_str: str):
    # 定义重试次数和重试间隔时间
    retry_count = 5
    retry_interval = 0.5

    # 定义当前重试次数和报错次数
    current_retry = 0
    error_count = 0

    while current_retry < retry_count:
        try:
            # 打开目标网页
            await page.goto(f"https://poe.com/{botname}")
            text = "This bot has been deleted for violating our"
            content = await page.content()
            if text in content:
                return "banned"
            if "0 free" in content:
                return "limited"
            # 找到输入框元素
            input_box = await page.wait_for_selector(
                ".GrowingTextArea_textArea__eadlu", timeout=2000
            )

            # 将字符串发送到输入框中
            await input_box.fill(input_str)

            # 找到发送按钮元素并点击,容易点不到，多等一次
            await page.wait_for_selector("button.Button_primary__pIDjn", timeout=1000)
            send_button = await page.wait_for_selector(
                "button.Button_primary__pIDjn", timeout=1000
            )
            # await asyncio.sleep(0.5)
            await send_button.click()
            break
        except:
            # 如果出现超时异常，打印错误信息并稍等一段时间后重试
            error_count += 1
            if error_count >= 1:
                await asyncio.sleep(retry_interval)
            current_retry += 1
            continue
    if current_retry == retry_count:
        return False


async def get_message_async(page, botname, sleep, nosuggest=False):
    consecutive_errors = 0
    answer_lost = 0
    suggest_lost = 0
    while True:
        await asyncio.sleep(sleep)
        try:
            await page.reload()
            response = await page.content()
            text = "This bot has been deleted for violating"
            if text in response:
                return "banned"
            if "Message_errorBubble" in response:
                answer_lost += 1
            if answer_lost > 2:
                return False
            match_text = re.search(
                r'<script id="__NEXT_DATA__" type="application/json">*(.*?)</script>',
                response,
                re.DOTALL,
            )
            json_data_text = match_text.group(1)
            json_obj_text = json.loads(json_data_text)

            chat_list_raw = json_obj_text["props"]["pageProps"]["payload"][
                "chatOfBotDisplayName"
            ]["messagesConnection"]["edges"]

            chat_list_raw = [a["node"] for a in chat_list_raw]
            chat_list_text = [a["text"] for a in chat_list_raw]
            if chat_list_text[-1]:
                if nosuggest:
                    return chat_list_text, []
                else:
                    match_suggest = re.search(
                        r'<section class="ChatMessageSuggestedReplies_suggestedRepliesContainer__JgW12">*(.*?)</section>',
                        response,
                        re.DOTALL,
                    )
                    try:
                        string_list = re.findall(
                            r">\s*([^<>\n]+)\s*<", match_suggest.group(1)
                        )
                        if len(string_list) >= 4:
                            return chat_list_text, string_list[0:4]
                        if len(string_list) <= 1:
                            suggest_lost += 1
                        if suggest_lost > 2:
                            return chat_list_text, string_list
                    except:
                        suggest_lost += 1
        except:
            consecutive_errors += 1
            print(f"poe-chat：获取返回消息失败{consecutive_errors}次")
            if consecutive_errors >= 5:
                return False
        else:
            consecutive_errors = 0


# 发送并接受
async def poe_chat(botname, question, page, nosuggest=False):
    if botname == "NeevaAI":
        nosuggest = True
    result1 = await send_message_async(page, botname, question)
    if result1 == "banned":
        return "banned"
    elif result1 == "limited":
        return "limited"
    elif result1 == False:
        return False
    if poe_persistor.suggest_able == "False":
        nosuggest = True
    result2 = await get_message_async(page, botname, sleep=2, nosuggest=nosuggest)
    if isinstance(result2, tuple):
        answers, suggests = result2
        return answers[-1], suggests
    elif isinstance(result2, str):
        is_banned = result2
        return "banned"
    elif isinstance(result2, bool):
        is_got = result2
        return is_got


# 清空聊天记录
async def poe_clear(page, truename):
    retry = 0
    while(retry - 3):
        try:
            await page.goto(f"https://poe.com/{truename}")

            chevron_button = await page.wait_for_selector(
                '[class="Button_buttonBase__0QP_m Button_flat__1hj0f ChatBreakButton_button__EihE0 ChatMessageInputFooter_chatBreakButton__hqJ3v"]'
            )
            is_button_enabled = await chevron_button.is_enabled()
            if is_button_enabled:
                try:
                    await chevron_button.click()
                except:
                    pass
                try:
                    await chevron_button.click(timeout=2000)
                except:
                    pass
                re_is_button_enabled = await chevron_button.is_enabled()
                if not re_is_button_enabled:
                    return True
                else:
                    retry += 1
            else:
                return True
        except:
            retry += 1
    return False

# 创建机器人
async def poe_create(page, botname, base_bot_index, prompt, retries=2):
    try:
        for i in range(retries):
            await page.goto("https://poe.com/create_bot")

            # 定位输入框并清空原有的默认值
            name_input: ElementHandle = await page.wait_for_selector(
                'input[name="name"]'
            )
            await name_input.fill("")

            # 输入新的值
            await name_input.fill(botname)

            await page.wait_for_selector('select[name="baseBot"]')

            if base_bot_index == 1:
                value = "chinchilla"
            elif base_bot_index == 2:
                value = "a2"
            # 根据索引选择选项
            await page.select_option(".Select_select__I0JvU", value=value)

            # 添加预设
            prompt_textarea = await page.wait_for_selector('textarea[name="prompt"]')
            await prompt_textarea.fill(prompt)

            chevron_button = await page.wait_for_selector(
                '[class="BotInfoForm_chevronDown__LFWWC"]'
            )
            await chevron_button.click()

            # 点击"Suggest replies"复选框的<label>元素
            checkbox_label: ElementHandle = await page.wait_for_selector(
                '//div[contains(text(), "Suggest replies")]/following-sibling::label'
            )
            await checkbox_label.click()

            # 点击"Linkify bot responses"复选框的<label>元素
            checkbox_label = await page.wait_for_selector(
                '//div[contains(text(), "Linkify bot responses")]/following-sibling::label'
            )
            await checkbox_label.click()

            # 点击"Create bot"按钮
            create_bot_button = await page.wait_for_selector(
                "button.Button_primary__pIDjn"
            )
            await create_bot_button.click()

            # 等待新页面加载完成
            try:
                await page.wait_for_selector(
                    "textarea.GrowingTextArea_textArea__eadlu", timeout=5000
                )
                return True
            except:
                pass

        return False
    except:
        return False


# 更改prompt
async def poe_change(page, truename, prompt):
    try:
        await page.goto(f"https://poe.com/edit_bot?bot={truename}")
        # 使用 prompt 来查找文本框
        prompt_input = await page.wait_for_selector(
            'textarea[name="prompt"]'
        )
        # 清空文本框并输入指定文本
        await prompt_input.fill("")
        await prompt_input.fill(prompt)

        # 使用 Save 来查找按钮
        save_button = await page.wait_for_selector(
            '[type="submit"]'
        )
        # 点击保存按钮
        await save_button.click()
        # 等待新页面加载完成
        try:
            await page.wait_for_selector(
                "textarea.GrowingTextArea_textArea__eadlu", timeout=5000
            )
            return True
        except:
            return False
    except:
        return False


# async def submit_email(page, email):
#     for i in range(5):
#         try:
#             await page.goto("https://poe.com")
#             # 点击 "Use email" 按钮
#             use_email_button = await page.query_selector('button:has-text("Use email")')
#             await use_email_button.click()

#             # 填写 email 地址
#             email_input = await page.wait_for_selector(
#                 "input.EmailInput_emailInput__4v_bn"
#             )
#             await email_input.fill(email)

#             # 点击 "Go" 按钮
#             go_button = await page.query_selector('button:has-text("Go")')
#             await go_button.click()

#             # 等待跳转并检查输入框是否存在
#             await page.wait_for_selector(
#                 "input.VerificationCodeInput_verificationCodeInput__YD3KV"
#             )
#             return True
#         except:
#             await page.reload()
#     return False


# async def submit_code(page, code, path):
#     retry_count = 0
#     while retry_count < 3:
#         try:
#             # 填写验证码
#             code_input = await page.wait_for_selector(
#                 "input.VerificationCodeInput_verificationCodeInput__YD3KV"
#             )
#             await code_input.fill("")  # 清空输入框
#             await code_input.fill(code)

#             # 点击 "Log In" 按钮
#             login_button = await page.query_selector('button:has-text("Log In")')
#             await login_button.click()

#             # 等待页面跳转，并检查页面是否有指定的输入框元素
#             await page.wait_for_selector(
#                 "textarea.ChatMessageInputView_textInput__Aervw"
#             )

#             # 获取当前页面的 cookie，并保存 poe.com 域名下的 cookie 到本地文件中
#             cookies = await page.context.cookies()
#             poe_cookies = [
#                 cookie for cookie in cookies if cookie["domain"] == "poe.com"
#             ]
#             if len(poe_cookies) > 0:
#                 with open(path, "w") as f:
#                     json.dump(poe_cookies[0], f)

#             return True
#         except:
#             # 如果页面上没有指定的输入框元素，就认为是失败了
#             if not await page.query_selector(
#                 "textarea.ChatMessageInputView_textInput__Aervw"
#             ):
#                 retry_count += 1
#                 # 等待一段时间后再次尝试输入验证码并点击 "Log In" 按钮
#                 await asyncio.sleep(1)
#             else:
#                 raise
#     return False
