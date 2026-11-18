# Диаграммы

Диаграммы Mermaid отображаются при просмотре Markdown на GitHub и описывают текущую реализацию.

## Архитектура

```mermaid
flowchart TD
    User[Пользователь] --> CLI[cli.py: main]
    JSON[Геометрия JSON] --> CLI
    CLI --> Core[core.py: generate]
    Core --> AI[model.py: predict / train]
    Core --> TFI[Трансфинитная интерполяция]
    Core --> Shapes[shapes.py: radial_grid]
    Core --> Ring[ellipses.py: ellipse_ring]
    AI --> Quality[core.py: quality]
    TFI --> Quality
    Shapes --> Quality
    Ring --> Quality
    Quality --> Result[Сетка, границы, отчёт]
    Result --> CLI
    CLI --> Export[export.py: write_mesh]
    Export --> Files[SU2 / VTK / blockMeshDict]
    CLI --> Plot[visualize.py: plot_mesh]
    Plot --> View[Изображение / интерактивное окно]
    CLI --> Report[JSON-отчёт в терминале]
```

## Последовательность построения

```mermaid
sequenceDiagram
    actor User as Пользователь
    participant CLI as cli.main
    participant Core as core.generate
    participant Model as model.predict
    participant Export as export.write_mesh
    participant Plot as visualize.plot_mesh
    User->>CLI: JSON, метод, формат, путь
    CLI->>CLI: Проверить пути и прочитать JSON
    CLI->>Core: generate(case, method)
    Core->>Core: Проверить параметры
    alt Метод ai для четырёхстороннего блока
        Core->>Model: predict(walls, horizontal, vertical)
        opt Первый вызов в процессе
            Model->>Model: Обучить и кешировать веса
        end
        Model-->>Core: Поле смещений
    else Метод tfi или radial
        Core->>Core: Геометрическое построение
    end
    Core->>Core: quality(grid)
    alt Качество допустимо
        Core-->>CLI: grid, patches, report
        CLI->>Export: Записать сетку
        Export-->>CLI: Файл сохранён
        opt Указан plot или show
            CLI->>Plot: Визуализировать
            Plot-->>CLI: Изображение сохранено / окно закрыто
        end
        CLI-->>User: JSON-отчёт
    else Недопустимые ячейки
        Core-->>CLI: ValueError
        CLI-->>User: Сообщение, код 2
    end
```

Ошибки параметров могут завершить проверку до построения. Ошибки файловой системы и визуализации обрабатываются отдельно от проверки качества; сетка может быть сохранена до ошибки изображения.

[Описание](overview.md) · [Требования](requirements.md) · [Сценарии](use-cases.md) · [README](../../README.md)
