
import pytest
import time
import os
from playwright.sync_api import sync_playwright, expect

BASE_URL = "https://demoqa.com"
TEXT_BOX_URL = f"{BASE_URL}/text-box"
CHECK_BOX_URL = f"{BASE_URL}/checkbox"
RADIO_BUTTON_URL = f"{BASE_URL}/radio-button"
WEB_TABLES_URL = f"{BASE_URL}/webtables"
BUTTONS_URL = f"{BASE_URL}/buttons"
DYNAMIC_PROPERTIES_URL = f"{BASE_URL}/dynamic-properties"

USER_DATA = {
    "full_name": "John Doe",
    "email": "johndoe@example.com",
    "current_address": "123 Main Street, City",
    "permanent_address": "456 Park Avenue, Town"
}


@pytest.fixture
def page():

    with sync_playwright() as playwright:
        browser = playwright.chromium.launch(
            headless=False)
        page = browser.new_page()

        page.set_viewport_size({"width": 1920, "height": 1080})

        yield page

        browser.close()


def scroll_to_element(page, selector):
    """
    Прокручивает страницу до указанного элемента.
    """
    page.evaluate(f'document.querySelector("{selector}").scrollIntoView()')
    time.sleep(0.5)


def test_text_box_form(page):
    """
    Tест проверяет заполнение и отправку формы Text Box
    с последующей проверкой отображения введенных данных.
    """

    page.goto(TEXT_BOX_URL)

    page.fill("#userName", USER_DATA["full_name"])
    page.fill("#userEmail", USER_DATA["email"])
    page.fill("#currentAddress", USER_DATA["current_address"])
    page.fill("#permanentAddress", USER_DATA["permanent_address"])

    scroll_to_element(page, "#submit")
    page.click("#submit")

    output = page.locator(".border")
    expect(output).to_be_visible()

    expect(page.locator("#name")).to_contain_text(USER_DATA["full_name"])
    expect(page.locator("#email")).to_contain_text(USER_DATA["email"])
    expect(page.locator(".border #currentAddress")).to_contain_text(USER_DATA["current_address"])
    expect(page.locator(".border #permanentAddress")).to_contain_text(USER_DATA["permanent_address"])


def test_check_box(page):
    """
    Тест проверяет выбор и состояние чекбоксов
    в древовидной структуре.
    """

    page.goto(CHECK_BOX_URL)

    page.click(".rct-collapse-btn")

    page.click("//span[text()='Desktop']/..//span[@class='rct-checkbox']")

    result_text = page.locator(".display-result")
    expect(result_text).to_be_visible()
    expect(result_text).to_contain_text("desktop")
    expect(result_text).to_contain_text("notes")
    expect(result_text).to_contain_text("commands")

    page.click("//span[text()='Documents']/..//span[@class='rct-checkbox']")

    expect(result_text).to_contain_text("documents")
    expect(result_text).to_contain_text("workspace")
    expect(result_text).to_contain_text("office")


def test_radio_button(page):
    """
    Тест проверяет выбор радиокнопок и
    отображение соответствующего сообщения.
    """

    page.goto(RADIO_BUTTON_URL)

    page.click("//label[@for='yesRadio']")

    success_text = page.locator(".text-success")
    expect(success_text).to_be_visible()
    expect(success_text).to_have_text("Yes")

    page.click("//label[@for='impressiveRadio']")

    expect(success_text).to_be_visible()
    expect(success_text).to_have_text("Impressive")

    no_radio = page.locator("#noRadio")
    expect(no_radio).to_be_disabled()


def test_web_tables(page):
    """
    Тест проверяет добавление, редактирование и удаление
    записей в веб-таблице.
    """

    new_user = {
        "firstName": "Michael",
        "lastName": "Smith",
        "email": "michaelsmith@example.com",
        "age": "35",
        "salary": "6000",
        "department": "QA"
    }

    edited_data = {
        "firstName": "Michael",
        "lastName": "Johnson",
        "email": "michaeljohnson@example.com",
        "age": "36",
        "salary": "7000",
        "department": "Development"
    }

    page.goto(WEB_TABLES_URL)

    page.click("#addNewRecordButton")

    page.fill("#firstName", new_user["firstName"])
    page.fill("#lastName", new_user["lastName"])
    page.fill("#userEmail", new_user["email"])
    page.fill("#age", new_user["age"])
    page.fill("#salary", new_user["salary"])
    page.fill("#department", new_user["department"])

    page.click("#submit")

    page.wait_for_selector(f"//div[contains(@class, 'rt-tbody')]//div[contains(text(), '{new_user['email']}')]")

    edit_button = page.locator(f"//div[contains(text(), '{new_user['email']}')]/following::div//span[@title='Edit']")
    edit_button.click()

    page.fill("#firstName", edited_data["firstName"])
    page.fill("#lastName", edited_data["lastName"])
    page.fill("#userEmail", edited_data["email"])
    page.fill("#age", edited_data["age"])
    page.fill("#salary", edited_data["salary"])
    page.fill("#department", edited_data["department"])

    page.click("#submit")

    page.wait_for_selector(f"//div[contains(@class, 'rt-tbody')]//div[contains(text(), '{edited_data['email']}')]")

    delete_button = page.locator(
        f"//div[contains(text(), '{edited_data['email']}')]/following::div//span[@title='Delete']")
    delete_button.click()

    expect(page.locator(f"//div[contains(text(), '{edited_data['email']}')]")).to_have_count(0)


def test_buttons(page):
    """
    Тест проверяет разные варианты клика по кнопкам:
    обычный клик, двойной клик и клик правой кнопкой мыши.
    """

    page.goto(BUTTONS_URL)

    double_click_button = page.locator("#doubleClickBtn")
    double_click_button.dblclick()

    expect(page.locator("#doubleClickMessage")).to_be_visible()
    expect(page.locator("#doubleClickMessage")).to_have_text("You have done a double click")

    right_click_button = page.locator("#rightClickBtn")
    right_click_button.click(button="right")

    expect(page.locator("#rightClickMessage")).to_be_visible()
    expect(page.locator("#rightClickMessage")).to_have_text("You have done a right click")

    page.click("//button[text()='Click Me']")

    expect(page.locator("#dynamicClickMessage")).to_be_visible()
    expect(page.locator("#dynamicClickMessage")).to_have_text("You have done a dynamic click")


def test_dynamic_properties(page):
    """
    Тест проверяет элементы с динамическими свойствами:
    кнопка, которая становится активной через 5 секунд,
    кнопка, которая меняет цвет, и кнопка, которая появляется через 5 секунд.
    """

    page.goto(DYNAMIC_PROPERTIES_URL)

    will_enable_button = page.locator("#enableAfter")
    expect(will_enable_button).to_be_disabled()

    page.wait_for_selector("#enableAfter:not([disabled])")

    expect(will_enable_button).to_be_enabled()

    color_change_button = page.locator("#colorChange")

    page.wait_for_function("""
        () => {
            const button = document.querySelector('#colorChange');
            const style = window.getComputedStyle(button);
            return style.color === 'rgb(220, 53, 69)';
        }
    """)

    visible_after_button = page.locator("#visibleAfter")

    if not visible_after_button.is_visible():
        page.wait_for_selector("#visibleAfter", state="visible")

    expect(visible_after_button).to_be_visible()


def test_upload_and_download(page):
    """
    Тест проверяет функциональность загрузки и скачивания файлов.
    """

    UPLOAD_DOWNLOAD_URL = f"{BASE_URL}/upload-download"

    page.goto(UPLOAD_DOWNLOAD_URL)

    test_file_path = "test_upload.txt"
    with open(test_file_path, "w") as f:
        f.write("This is a test file content for upload testing.")

    file_input = page.locator("#uploadFile")
    file_input.set_input_files(test_file_path)

    upload_result = page.locator("#uploadedFilePath")
    expect(upload_result).to_be_visible()
    expect(upload_result).to_contain_text("test_upload.txt")

    os.remove(test_file_path)

    download_button = page.locator("#downloadButton")
    expect(download_button).to_be_visible()


def test_modal_dialogs(page):
    """
    Тест проверяет работу с модальными диалогами:
    маленький и большой диалоги.
    """

    MODAL_DIALOGS_URL = f"{BASE_URL}/modal-dialogs"

    page.goto(MODAL_DIALOGS_URL)

    page.click("#showSmallModal")

    small_modal = page.locator(".modal-content")
    expect(small_modal).to_be_visible()

    expect(page.locator(".modal-title")).to_have_text("Small Modal")
    expect(page.locator(".modal-body")).to_contain_text("This is a small modal")

    page.click("#closeSmallModal")

    expect(small_modal).to_have_count(0)

    page.click("#showLargeModal")

    large_modal = page.locator(".modal-content")
    expect(large_modal).to_be_visible()

    expect(page.locator(".modal-title")).to_have_text("Large Modal")

    page.click("#closeLargeModal")

    expect(large_modal).to_have_count(0)


from playwright.sync_api import sync_playwright
import tempfile

def test_practice_form():
    with sync_playwright() as p:

        browser = p.chromium.launch(headless=False)
        page = browser.new_page()
        page.goto("https://demoqa.com/automation-practice-form")
        page.fill("#firstName", "Rustam")
        page.fill("#lastName", "Nagaev")
        page.fill("#userEmail", "rustik@xxx.com")
        page.click("label[for='gender-radio-1']")
        page.fill("#userNumber", "1234567890")
        page.click("#dateOfBirthInput")
        page.fill("#dateOfBirthInput", "06 May 1990")
        page.press("#dateOfBirthInput", "Enter")
        page.fill("#subjectsInput", "Maths")
        page.press("#subjectsInput", "Enter")
        page.click("label[for='hobbies-checkbox-1']")

        with tempfile.NamedTemporaryFile(suffix=".jpg") as tmp_file:

            tmp_file.write(b"Fake image content for testing")
            tmp_file.flush()

            page.set_input_files("#uploadPicture", tmp_file.name)

        page.fill("#currentAddress", "1234 Elm Street")
        page.click("#state")
        page.fill("#react-select-3-input", "NCR")
        page.press("#react-select-3-input", "Enter")
        page.click("#city")
        page.fill("#react-select-4-input", "Delhi")
        page.press("#react-select-4-input", "Enter")
        page.click("#submit")
        page.wait_for_selector("#example-modal-sizes-title-lg")
        modal_content = page.inner_text(".table-responsive")

        assert "Rustam Nagaev" in modal_content
        assert "rustik@xxx.com" in modal_content
        assert "1234567890" in modal_content
        assert "06 May,1990" in modal_content
        assert "Maths" in modal_content
        assert "Sports" in modal_content
        assert "1234 Elm Street" in modal_content
        assert "NCR Delhi" in modal_content


        browser.close()



