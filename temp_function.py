def display_grv_interface(lang: str = 'ru'):
    """
    Отображение интерфейса для работы с ГРВ-изображениями в Streamlit.
    Упрощенная версия для работы только с загрузкой файлов ГРВ-грамм без подключения к физической камере.
    Удалены функции фото ауры и просмотра органов из раздела ГРВ.
    
    Args:
        lang (str): Язык интерфейса ('ru' или 'en')
    """
    # Импортируем необходимые библиотеки
    import streamlit as st
    import matplotlib.pyplot as plt
    
    # Сбрасываем флаг загрузки сессии при новом рендеринге страницы
    # Но делаем это только если этот рендеринг не был вызван загрузкой сессии
    if 'session_loaded' in st.session_state and st.session_state.session_loaded:
        # Если сессия была загружена, оставляем флаг,
        # чтобы избежать бесконечной перезагрузки
        pass
    else:
        # Сбрасываем флаг session_loaded
        st.session_state.session_loaded = False
        
    st.title("Анализ ГРВ-грамм" if lang == 'ru' else "GRV-gram Analysis")
    
    # Показываем информацию о работе с загрузкой снимков
    st.info(
        "Загрузите имеющиеся ГРВ-граммы для каждого пальца обеих рук для получения энергетической модели." if lang == 'ru' else
        "Upload existing GRV-grams for each finger of both hands to get an energy model."
    )
    
    # Инициализация GRV-процессора, если он еще не инициализирован
    if 'grv_camera' not in st.session_state:
        st.session_state.grv_camera = GRVCamera(lang=lang)
    
    grv = st.session_state.grv_camera
    
    # Верхние кнопки управления
    col1, col2, col3 = st.columns(3)
    
    # Кнопка очистки
    if col3.button("Очистить все" if lang == 'ru' else "Clear all"):
        # Инициализируем заново все изображения пальцев
        grv.finger_images = {
            HandType.LEFT: {ft: None for ft in FingerType},
            HandType.RIGHT: {ft: None for ft in FingerType}
        }
        grv.processed_data = {
            HandType.LEFT: {ft: {} for ft in FingerType},
            HandType.RIGHT: {ft: {} for ft in FingerType}
        }
        st.success("Данные очищены" if lang == 'ru' else "Data cleared")
    
    # Выбор руки и пальца
    col1, col2 = st.columns(2)
    
    hand_options = {
        HandType.LEFT: "Левая рука" if lang == 'ru' else "Left hand",
        HandType.RIGHT: "Правая рука" if lang == 'ru' else "Right hand"
    }
    
    finger_options = {
        FingerType.THUMB: "Большой" if lang == 'ru' else "Thumb",
        FingerType.INDEX: "Указательный" if lang == 'ru' else "Index",
        FingerType.MIDDLE: "Средний" if lang == 'ru' else "Middle",
        FingerType.RING: "Безымянный" if lang == 'ru' else "Ring",
        FingerType.PINKY: "Мизинец" if lang == 'ru' else "Pinky"
    }
    
    selected_hand_label = col1.selectbox("Выберите руку:" if lang == 'ru' else "Select hand:", list(hand_options.values()))
    selected_hand = list(hand_options.keys())[list(hand_options.values()).index(selected_hand_label)]
    
    selected_finger_label = col2.selectbox("Выберите палец:" if lang == 'ru' else "Select finger:", list(finger_options.values()))
    selected_finger = list(finger_options.keys())[list(finger_options.values()).index(selected_finger_label)]
    
    # Загрузка ГРВ-изображения
    st.subheader("Загрузка ГРВ-граммы" if lang == 'ru' else "Upload GRV-gram")
    
    # Информация и подсказка по формату загружаемых файлов
    st.markdown(
        "Файлы ГРВ-грамм должны быть в формате BMP, JPEG или PNG. "
        "Рекомендуется использовать снимки, полученные с помощью программы РОК ГРВ-сканер." if lang == 'ru' else
        "GRV-gram files should be in BMP, JPEG or PNG format. "
        "It is recommended to use images obtained using the ROK GRV-scanner program."
    )
    
    uploaded_file = st.file_uploader(
        "Выберите файл ГРВ-граммы" if lang == 'ru' else "Choose a GRV-gram file", 
        type=["bmp", "jpg", "jpeg", "png"],
        key=f"grv_upload_{selected_hand.name}_{selected_finger.name}"
    )
    
    if uploaded_file is not None:
        # Обработка загруженного изображения
        process_uploaded_grv_image(grv, uploaded_file, selected_hand, selected_finger, lang, finger_options)
    
    # Панель состояния - показываем, какие пальцы уже отсканированы
    st.subheader("Статус загрузки ГРВ-грамм" if lang == 'ru' else "GRV-gram Upload Status")
    
    # Создаем сетку для отображения статуса
    hand_cols = st.columns(2)
    
    for i, hand in enumerate([HandType.LEFT, HandType.RIGHT]):
        with hand_cols[i]:
            st.write(hand_options[hand])
            finger_cols = st.columns(5)
            
            for j, finger in enumerate(FingerType):
                with finger_cols[j]:
                    if grv.finger_images[hand][finger] is not None:
                        st.success(finger_options[finger])
                    else:
                        st.error(finger_options[finger])
    
    # Кнопки для анализа и сохранения/загрузки
    st.subheader("Анализ и управление данными" if lang == 'ru' else "Analysis and Data Management")
    col1, col2, col3 = st.columns(3)
    
    # Кнопка для отображения базовой визуализации, доступна если данные уже есть в session_state
    if "chakra_values_from_grv" in st.session_state and col3.button("Показать визуализацию" if lang == 'ru' else "Show visualization", key="button_show_viz_main"):
        # Импортируем модули для визуализации
        from chakra_visualization import create_chakra_visualization
        from chakra_visualization_3d import create_chakra_visualization_3d
        
        # Берем данные из session_state
        energy_values = st.session_state.chakra_values_from_grv
        
        # Создаем 2D визуализацию чакр
        st.subheader("2D Визуализация чакр" if lang == 'ru' else "2D Chakra Visualization")
        fig_2d = create_chakra_visualization(energy_values, lang)
        st.pyplot(fig_2d)
        
        # Создаем 3D визуализацию чакр
        st.subheader("3D Визуализация чакр" if lang == 'ru' else "3D Chakra Visualization")
        fig_3d = create_chakra_visualization_3d(energy_values, lang)
        st.plotly_chart(fig_3d, use_container_width=True)
        
    # Кнопка анализа
    if col1.button("Анализировать" if lang == 'ru' else "Analyze"):
        # Проверяем, все ли пальцы отсканированы
        all_scanned = True
        for hand in HandType:
            for finger in FingerType:
                if grv.finger_images[hand][finger] is None:
                    all_scanned = False
                    break
        
        if not all_scanned:
            st.warning("Не все пальцы загружены. Для полного анализа загрузите ГРВ-граммы всех пальцев." if lang == 'ru' else 
                      "Not all fingers have been uploaded. For a complete analysis, upload GRV-grams of all fingers.")
        else:
            with st.spinner("Обработка изображений..." if lang == 'ru' else "Processing images..."):
                # Обрабатываем все изображения
                energy_model = grv.process_all_fingers()
                
                if "error" in energy_model:
                    st.error("Ошибка при обработке данных" if lang == 'ru' else "Error processing data")
                else:
                    # Показываем результаты анализа
                    st.success("Подготовка результатов анализа..." if lang == 'ru' else "Preparing analysis results...")
                    
                    # Отображаем значения энергии чакр
                    st.subheader("Энергетическая модель" if lang == 'ru' else "Energy Model")
                    
                    # Передаем данные в основное приложение через состояние сессии
                    st.session_state.chakra_values_from_grv = energy_model["chakra_values"]
                    
                    # Отображаем гистограмму значений чакр
                    fig, ax = plt.subplots(figsize=(10, 5))
                    chakras = list(energy_model["chakra_values"].keys())
                    values = list(energy_model["chakra_values"].values())
                    
                    ax.bar(chakras, values, color=['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'])
                    ax.set_ylim(0, 100)
                    ax.set_ylabel("Энергия (%)" if lang == 'ru' else "Energy (%)")
                    ax.set_title("Энергетический баланс чакр" if lang == 'ru' else "Chakra Energy Balance")
                    
                    st.pyplot(fig)
                    
                    # Отображаем индекс баланса
                    st.metric(
                        "Индекс баланса" if lang == 'ru' else "Balance Index", 
                        f"{energy_model['balance_index']:.2f}%"
                    )
                    
                    # Уведомление о готовности данных
                    st.success("Данные обработаны и готовы к использованию в основном приложении." if lang == 'ru' else 
                             "Data processed and ready for use in the main application.")
                    
                    # Добавляем кнопку для создания и отображения базовой визуализации
                    if st.button("Показать визуализацию" if lang == 'ru' else "Show Visualization", key="button_show_viz_analysis"):
                        # Визуализация чакр
                        st.subheader("Визуализация чакр" if lang == 'ru' else "Chakra Visualization")
                        
                        # Используем функцию из chakra_visualization
                        from chakra_visualization import create_chakra_visualization
                        
                        # Создаем визуализацию чакр
                        fig_chakra = create_chakra_visualization(energy_model["chakra_values"], lang)
                        st.pyplot(fig_chakra)
                        
                        # Добавляем детальную информацию о чакрах
                        st.subheader("Детальная информация о чакрах" if lang == 'ru' else "Detailed Chakra Information")
                        
                        # Получаем детальную информацию о каждой чакре
                        chakra_details = grv.get_energy_details(energy_model["chakra_values"])
                        
                        # Отображаем информацию в аккордеоне для каждой чакры
                        for chakra_name, details in chakra_details.items():
                            with st.expander(f"{chakra_name} - {details['status']}"):
                                st.write(f"**Энергия:** {details['energy']:.1f}%")
                                st.write(f"**Состояние:** {details['status']}")
                                st.write(f"**Описание:** {details['description']}")
    
    # Блок для сохранения и загрузки сессии
    st.subheader("Сохранение и загрузка сессии" if lang == 'ru' else "Save and Load Session")
    
    # Информационное сообщение
    st.info(
        "Сессия сохраняется в файл, который вы можете скачать и загрузить позже, чтобы не повторять загрузку ГРВ-грамм." if lang == 'ru' else
        "The session is saved to a file that you can download and upload later to avoid repeating the upload of GRV-grams."
    )
    
    save_col1, save_col2 = st.columns(2)
    
    # Поле для ввода имени файла для сохранения
    with save_col1:
        save_filename = st.text_input(
            "Имя файла для сохранения" if lang == 'ru' else "Filename for saving", 
            value="grv_session.json"
        )
        
        # Кнопка сохранения
        if st.button("Сохранить сессию" if lang == 'ru' else "Save session"):
            if grv.save_session(save_filename):
                # Подготавливаем ссылку на скачивание файла
                import base64
                import os
                if os.path.exists(save_filename):
                    with open(save_filename, "rb") as file:
                        file_content = file.read()
                        b64_content = base64.b64encode(file_content).decode()
                        
                        download_href = f'<a href="data:application/octet-stream;base64,{b64_content}" download="{save_filename}">Скачать файл сессии</a>'
                        st.markdown(download_href, unsafe_allow_html=True)
                        
                        st.success(
                            f"Сессия успешно сохранена в файл {save_filename}. Нажмите на ссылку выше для скачивания." if lang == 'ru' else 
                            f"Session successfully saved to file {save_filename}. Click the link above to download."
                        )
                else:
                    st.error(
                        f"Файл {save_filename} не найден после сохранения" if lang == 'ru' else 
                        f"File {save_filename} not found after saving"
                    )
    
    # Блок для загрузки сессии
    with save_col2:
        # Файловый загрузчик для выбора файла сессии
        uploaded_session = st.file_uploader(
            "Выберите файл сессии для загрузки" if lang == 'ru' else "Choose a session file to load",
            type=["json", "dat"],
            key="session_uploader"
        )
        
        if uploaded_session is not None:
            # Сохраняем загруженный файл во временный файл
            import os
            import tempfile
            
            # Создаем временный файл для сохранения загруженного файла
            temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=".json")
            temp_file.write(uploaded_session.getvalue())
            temp_file.close()
            
            # Важно: передаем полный путь к временному файлу
            session_file_path = temp_file.name
            print(f"Попытка загрузки сессии из: {session_file_path}")
            
            # Загружаем сессию из временного файла, проверяя что файл существует
            if os.path.exists(session_file_path) and grv.load_session(session_file_path):
                st.success(
                    f"Сессия успешно загружена из файла {uploaded_session.name}" if lang == 'ru' else 
                    f"Session successfully loaded from file {uploaded_session.name}"
                )
                
                # Обновляем статус загрузки в интерфейсе
                st.subheader("Загруженные данные" if lang == 'ru' else "Loaded Data")
                
                # Показываем загруженные изображения
                loaded_images_count = 0
                for hand in HandType:
                    for finger in FingerType:
                        if grv.finger_images[hand][finger] is not None:
                            loaded_images_count += 1
                
                st.info(
                    f"Загружено {loaded_images_count} из 10 ГРВ-грамм" if lang == 'ru' else
                    f"Loaded {loaded_images_count} out of 10 GRV-grams"
                )
                
                # Если есть загруженные данные по чакрам, показываем их
                if "chakra_values_from_grv" in st.session_state:
                    energy_values = st.session_state.chakra_values_from_grv
                    
                    # Отображаем энергетический баланс
                    st.subheader("Энергетическая модель" if lang == 'ru' else "Energy Model")
                    
                    # Отображаем гистограмму значений чакр
                    import matplotlib.pyplot as plt
                    fig, ax = plt.subplots(figsize=(10, 5))
                    chakras = list(energy_values.keys())
                    values = list(energy_values.values())
                    
                    ax.bar(chakras, values, color=['red', 'orange', 'yellow', 'green', 'blue', 'indigo', 'violet'])
                    ax.set_ylim(0, 100)
                    ax.set_ylabel("Энергия (%)" if lang == 'ru' else "Energy (%)")
                    ax.set_title("Энергетический баланс чакр" if lang == 'ru' else "Chakra Energy Balance")
                    
                    st.pyplot(fig)
                    
                    # Рассчитываем индекс баланса
                    balance_index = grv.calculate_balance_index(energy_values)
                    
                    # Отображаем индекс баланса
                    st.metric(
                        "Индекс баланса" if lang == 'ru' else "Balance Index", 
                        f"{balance_index:.2f}%"
                    )
                    
                    # Добавляем кнопку для отображения визуализации
                    if st.button("Показать визуализацию" if lang == 'ru' else "Show visualization", key="button_show_viz_load"):
                        # Импортируем модули для визуализации
                        from chakra_visualization import create_chakra_visualization
                        from chakra_visualization_3d import create_chakra_visualization_3d
                        
                        # Создаем 2D визуализацию чакр
                        st.subheader("2D Визуализация чакр" if lang == 'ru' else "2D Chakra Visualization")
                        fig_2d = create_chakra_visualization(energy_values, lang)
                        st.pyplot(fig_2d)
                        
                        # Создаем 3D визуализацию чакр
                        st.subheader("3D Визуализация чакр" if lang == 'ru' else "3D Chakra Visualization")
                        fig_3d = create_chakra_visualization_3d(energy_values, lang)
                        st.plotly_chart(fig_3d, use_container_width=True)