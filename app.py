import streamlit as st
import os
from PIL import Image
import pandas as pd
from datetime import datetime
import gdown
import zipfile
import tempfile
import shutil


top_options = [
   'куртка', 'плащ', 'жилет', 'пиджак', 'кардиган', 'косуха', 'худи', 'рубашка ДР', 'рубашка КР', 'футболка',
    'майка', 'свитер', 'блузка', 'кофта', 'платье ДР', 'платье КР', 'комбинезон'
]

bottom_options = [
    "платье ДР", "платье КР", "шорты", "брюки", "джинсы", "юбка Д", "юбка К", "штаны",
]

head_options = [
    "шляпа", "кепка", "панама", "платок", "шапка"
]

shoes_options = [
    "туфли", "кроссовки", "кеды", "cандалии", "шлепанцы", 'ботинки'
]

accessoires_options = [
    "зонт", "солнечные очки", "шарф", "перчатки", 'дождевик'
]

st.set_page_config(page_title="Разметка изображений", layout="wide")

# Компактные стили CSS с цветными заголовками
st.markdown("""
<style>
    /* Убираем большой отступ сверху */
    .main .block-container {
        padding-top: 1rem !important;
        padding-bottom: 1rem !important;
    }

    /* Уменьшаем отступы у чекбоксов */
    .stCheckbox {
        margin-bottom: -10px !important;
    }

    /* Компактные радиокнопки */
    .stRadio > div {
        gap: 0.5rem !important;
    }

    /* Убираем лишние отступы */
    .element-container {
        margin-bottom: 0.5rem !important;
    }

    /* Компактные заголовки */
    .stMarkdown h3 {
        margin-top: 0.5rem !important;
        margin-bottom: 0.2rem !important;
    }

    /* Цветные заголовки категорий */
    .category-title-person { color: #1976D2; font-weight: bold; }
    .category-title-clothing { color: #7B1FA2; font-weight: bold; }
    .category-title-accessories { color: #388E3C; font-weight: bold; }
</style>
""", unsafe_allow_html=True)


# Функция для загрузки изображений из Google Drive
@st.cache_data
def load_images_from_gdrive(gdrive_url, folder_name):
    """Загружает изображения из Google Drive по ссылке"""
    try:
        # Создаем временную директорию
        temp_dir = tempfile.mkdtemp()

        # Извлекаем ID из ссылки Google Drive
        if 'drive.google.com' in gdrive_url:
            if '/folders/' in gdrive_url:
                folder_id = gdrive_url.split('/folders/')[1].split('?')[0]
                # Для папок используем другой подход
                st.error("Пожалуйста, используйте прямую ссылку на ZIP архив, а не на папку")
                return None, None
            elif '/file/d/' in gdrive_url:
                file_id = gdrive_url.split('/file/d/')[1].split('/')[0]
            else:
                st.error("Неверный формат ссылки Google Drive")
                return None, None
        else:
            st.error("Ссылка должна быть из Google Drive")
            return None, None

        # Скачиваем файл
        zip_path = os.path.join(temp_dir, "images.zip")
        download_url = f"https://drive.google.com/uc?id={file_id}"

        with st.spinner("Загружаем изображения..."):
            gdown.download(download_url, zip_path, quiet=False)

        # Распаковываем
        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        # Находим изображения (игнорируем служебные файлы macOS)
        images = []
        image_paths = {}

        for root, dirs, files in os.walk(extract_dir):
            # Пропускаем папки __MACOSX
            if '__MACOSX' in root:
                continue

            for file in files:
                # Пропускаем служебные файлы macOS
                if file.startswith('._') or file.startswith('.DS_Store'):
                    continue

                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    full_path = os.path.join(root, file)
                    # Проверяем, что файл действительно можно открыть как изображение
                    try:
                        with Image.open(full_path) as test_img:
                            test_img.verify()  # Проверяем целостность
                        images.append(file)
                        image_paths[file] = full_path
                    except Exception as e:
                        print(f"Пропускаем поврежденный файл {file}: {e}")

        return images, image_paths

    except Exception as e:
        st.error(f"Ошибка загрузки: {e}")
        return None, None


# Боковая панель
st.sidebar.header("📂 Загрузка изображений")

# Способ 1: Google Drive ссылка
gdrive_url = st.sidebar.text_input(
    "🔗 Ссылка на ZIP архив в Google Drive:",
    placeholder="https://drive.google.com/file/d/...",
    help="Создайте ZIP архив с изображениями, загрузите на Google Drive и вставьте ссылку"
)

dataset_name = st.sidebar.text_input(
    "📁 Название датасета:",
    placeholder="dataset1",
    help="Короткое название для файла результатов"
)

# Способ 2: Загрузка файлов напрямую
st.sidebar.markdown("**Или загрузите ZIP файл:**")
uploaded_zip = st.sidebar.file_uploader(
    "Выберите ZIP архив с изображениями",
    type=['zip']
)

# Имя разметчика
st.sidebar.markdown("---")
st.sidebar.header("👤 Разметчик")
annotator_name = st.sidebar.text_input("Ваше имя:", placeholder="Например: Женя",
                                       help="Имя будет добавлено в название файла")

# Инструкция
st.sidebar.markdown("---")
st.sidebar.header("📋 Инструкция")
st.sidebar.markdown("""
**Подготовка:**
1. Создайте ZIP архив с изображениями
2. Загрузите на Google Drive и получите ссылку
3. Вставьте ссылку выше и укажите название

**Разметка:**
- Для каждого человека выберите пол, возраст, одежду
- Нажимайте "➕ Добавить человека"
- Переходите между фото кнопками ⬅️ ➡️

**Экспорт:**
- Скачайте CSV файл в конце работы
""")

# Загрузка изображений
images = None
image_paths = None

if gdrive_url and dataset_name:
    images, image_paths = load_images_from_gdrive(gdrive_url, dataset_name)
elif uploaded_zip:
    try:
        temp_dir = tempfile.mkdtemp()
        zip_path = os.path.join(temp_dir, "uploaded.zip")

        with open(zip_path, "wb") as f:
            f.write(uploaded_zip.getvalue())

        extract_dir = os.path.join(temp_dir, "extracted")
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            zip_ref.extractall(extract_dir)

        images = []
        image_paths = {}

        for root, dirs, files in os.walk(extract_dir):
            # Пропускаем папки __MACOSX
            if '__MACOSX' in root:
                continue

            for file in files:
                # Пропускаем служебные файлы macOS
                if file.startswith('._') or file.startswith('.DS_Store'):
                    continue

                if file.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp')):
                    full_path = os.path.join(root, file)
                    # Проверяем, что файл действительно можно открыть как изображение
                    try:
                        with Image.open(full_path) as test_img:
                            test_img.verify()  # Проверяем целостность
                        images.append(file)
                        image_paths[file] = full_path
                    except Exception as e:
                        print(f"Пропускаем поврежденный файл {file}: {e}")

        if not dataset_name:
            dataset_name = "uploaded_images"

    except Exception as e:
        st.error(f"Ошибка обработки файла: {e}")

if not images:
    st.info("👆 Загрузите изображения через боковую панель")
    st.markdown("""
    ### 📝 Как подготовить данные:

    **Способ 1: Google Drive (рекомендуется)**
    1. Создайте ZIP архив с изображениями
    2. Загрузите на Google Drive  
    3. Откройте доступ "Просмотр для всех, у кого есть ссылка"
    4. Скопируйте ссылку и вставьте выше

    **Способ 2: Прямая загрузка**
    1. Создайте ZIP архив с изображениями
    2. Загрузите через кнопку "Выберите ZIP архив"
    """)
    st.stop()

# Состояние сессии
if 'current_idx' not in st.session_state:
    st.session_state.current_idx = 0
if 'annotations' not in st.session_state:
    st.session_state.annotations = {}
if 'form_counter' not in st.session_state:
    st.session_state.form_counter = 0


# Функция для сброса формы
def reset_form():
    st.session_state.form_counter += 1


# Сброс формы при изменении изображения
if 'last_image' not in st.session_state or st.session_state.last_image != images[st.session_state.current_idx]:
    st.session_state.last_image = images[st.session_state.current_idx]
    reset_form()

# Навигация
col1, col2, col3 = st.columns([1, 4, 1])
with col1:
    if st.button("⬅️ Назад", disabled=st.session_state.current_idx == 0):
        st.session_state.current_idx -= 1
        st.rerun()
with col3:
    if st.button("Вперед ➡️", disabled=st.session_state.current_idx >= len(images) - 1):
        st.session_state.current_idx += 1
        st.rerun()

# Отображение изображения и формы разметки
current_image = images[st.session_state.current_idx]
img_path = image_paths[current_image]

left_col, right_col = st.columns([2, 1])

with left_col:
    try:
        img = Image.open(img_path)
        st.image(img, caption=current_image, use_container_width=True)
        st.write(f"Изображение {st.session_state.current_idx + 1} из {len(images)}")
    except Exception as e:
        st.error(f"Ошибка загрузки изображения: {e}")

with right_col:
    st.subheader("Разметка")

    if current_image not in st.session_state.annotations:
        st.session_state.annotations[current_image] = []

    # ПОЛЯ ФОРМЫ
    counter = st.session_state.form_counter

    # Пол и Возраст в одной строке
    col1, col2 = st.columns(2)

    with col1:
        st.markdown('<p class="category-title-person">Пол:</p>', unsafe_allow_html=True)
        sex = st.radio("", ["М", "Ж"],
                       key=f"form_sex_{counter}", label_visibility="collapsed",
                       index=1, horizontal=True)

    with col2:
        st.markdown('<p class="category-title-person">Возраст:</p>', unsafe_allow_html=True)
        age = st.radio("", ["Ребенок", "Взрослый", "Пожилой"],
                       key=f"form_age_{counter}", label_visibility="collapsed",
                       index=1, horizontal=True)

    # Верх и Низ в одной строке
    col3, col4 = st.columns(2)

    with col3:
        st.markdown('<p class="category-title-clothing">Верх:</p>', unsafe_allow_html=True)
        top_selected = []
        for option in sorted(top_options):
            if st.checkbox(option, key=f"top_{option}_{counter}"):
                top_selected.append(option)

    with col4:
        st.markdown('<p class="category-title-clothing">Низ:</p>', unsafe_allow_html=True)
        bottom_selected = []
        for option in sorted(bottom_options):
            if st.checkbox(option, key=f"bottom_{option}_{counter}"):
                bottom_selected.append(option)

    # Обувь и Головной убор в одной строке
    col5, col6 = st.columns(2)

    with col5:
        st.markdown('<p class="category-title-accessories">Обувь:</p>', unsafe_allow_html=True)
        shoes_selected = []
        for option in sorted(shoes_options):
            if st.checkbox(option, key=f"shoes_{option}_{counter}"):
                shoes_selected.append(option)

    with col6:
        st.markdown('<p class="category-title-accessories">Головной убор:</p>', unsafe_allow_html=True)
        head_selected = []
        for option in sorted(head_options):
            if st.checkbox(option, key=f"head_{option}_{counter}"):
                head_selected.append(option)

    # Аксессуары
    st.markdown('<p class="category-title-accessories">Аксессуары:</p>', unsafe_allow_html=True)
    accessoires_selected = []
    for option in sorted(accessoires_options):
        if st.checkbox(option, key=f"accessoires_{option}_{counter}"):
            accessoires_selected.append(option)

    # КНОПКА ДОБАВИТЬ ЧЕЛОВЕКА
    if st.button("➕ Добавить человека", use_container_width=True):
        st.session_state.annotations[current_image].append({
            "photo_id": current_image,
            "sex": sex,
            "age": age,
            "top": top_selected,
            "bottom": bottom_selected,
            "shoes": shoes_selected,
            "head": head_selected,
            "accessoires": accessoires_selected
        })

        reset_form()
        st.success("Добавлено")
        st.rerun()

# Таблица текущих аннотаций
if st.session_state.annotations[current_image]:
    st.subheader("Размеченные люди")
    df = pd.DataFrame(st.session_state.annotations[current_image])
    st.dataframe(df)

# Экспорт
st.sidebar.markdown("---")
st.sidebar.header("💾 Экспорт")

if st.session_state.annotations:
    all_data = []
    for img, people in st.session_state.annotations.items():
        for person in people:
            all_data.append({
                "photo_id": img,
                "sex": person["sex"],
                "age": person["age"],
                "top": ", ".join(person["top"]),
                "bottom": ", ".join(person["bottom"]),
                "shoes": ", ".join(person["shoes"]),
                "head": ", ".join(person["head"]),
                "accessoires": ", ".join(person["accessoires"])
            })

    if all_data:
        df_export = pd.DataFrame(all_data)
        csv = df_export.to_csv(index=False, encoding='utf-8')

        # Формируем название файла
        name_part = annotator_name.strip() if annotator_name.strip() else "user"
        name_part = "".join(c for c in name_part if c.isalnum() or c in (' ', '-', '_')).strip()
        name_part = name_part.replace(' ', '_')

        folder_part = dataset_name if dataset_name else "dataset"
        annotated_images_count = len([img for img, people in st.session_state.annotations.items() if people])

        filename = f"{name_part}_{folder_part}_{annotated_images_count}.csv"

        st.sidebar.download_button(
            label="📥 Скачать CSV",
            data=csv,
            file_name=filename,
            mime="text/csv",
            use_container_width=True
        )

        st.sidebar.success(f"Готово: {len(all_data)} записей")
        st.sidebar.info(f"📄 `{filename}`")
    else:
        st.sidebar.info("Нет данных для экспорта")
else:
    st.sidebar.info("Нет размеченных изображений")