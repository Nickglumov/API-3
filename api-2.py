import requests
from urllib.parse import urlparse
from dotenv import load_dotenv
import os


def is_vk_short_link(token, vk_url):
    api_url = "https://api.vk.com/method/utils.getLinkStats"
    parsed_url = urlparse(vk_url)
    key = parsed_url.path.lstrip('/')
    params = {
        "v": "5.199",
        "access_token": token,
        "key": key,
        "interval": "day"
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    response_data = response.json()

    return "response" in response_data and "stats" in response_data["response"] and "error" not in response_data


def create_vk_short_link(token, original_url):
    api_url = "https://api.vk.com/method/utils.getShortLink"
    params = {
        "v": "5.199",
        "access_token": token,
        "url": original_url,
        "private": 0
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    response_data = response.json()

    if "error" in response_data:
        raise RuntimeError(f"VK API error: {response_data['error']}")

    return response_data["response"]["short_url"]


def get_total_clicks(token, short_url):
    api_url = "https://api.vk.com/method/utils.getLinkStats"
    parsed_url = urlparse(short_url)
    key = parsed_url.path.lstrip('/')
    params = {
        "v": "5.199",
        "access_token": token,
        "key": key,
        "interval": "day"
    }
    response = requests.get(api_url, params=params)
    response.raise_for_status()
    response_data = response.json()

    if "error" in response_data:
        raise RuntimeError(f"VK API error: {response_data['error']}")

    return sum(day["views"] for day in response_data["response"]["stats"])


def main():
    load_dotenv()
    vk_token = os.getenv("VK_TOKEN")
    if not vk_token:
        raise ValueError("Переменная окружения VK_TOKEN не найдена.")

    user_url = input("Введите ссылку: ").strip()
    if not user_url:
        raise ValueError("URL не может быть пустым")

    try:
        if is_vk_short_link(vk_token, user_url):
            total_views = get_total_clicks(vk_token, user_url)
            print(f"Количество кликов: {total_views}")
        else:
            short_url = create_vk_short_link(vk_token, user_url)
            print(f"Сокращенная ссылка: {short_url}")

    except requests.exceptions.RequestException as e:
        print(f"Ошибка HTTP-запроса: {e}")
    except RuntimeError as e:
        print(f"Ошибка VK API: {e}")
    except ValueError as e:
        print(f"Ошибка ввода: {e}")


if __name__ == "__main__":
    main()