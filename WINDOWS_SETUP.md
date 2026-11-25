# Запуск Mesh2D на Windows

Все команды выполняются в PowerShell. Проект использует Python и Poetry; OpenFOAM для построения и просмотра сеток не требуется.

## 1. Установить инструменты

Установите Python 3.11–3.14 с python.org (рекомендуется 3.11) и Git с git-scm.com. В установщике Python включите добавление Python в PATH. После установки откройте новое окно PowerShell.

Проверьте Python:

```powershell
py -3.11 --version
git --version
```

Если установлена другая поддерживаемая версия Python, замените `-3.11` в командах на её номер.

## 2. Скачать проект

```powershell
git clone https://github.com/Stolyan-2k/Development-of-an-AI-Based-Generator-of-Structured-2D-Meshes-from-Given-Geometry.git
cd Development-of-an-AI-Based-Generator-of-Structured-2D-Meshes-from-Given-Geometry
```

Если проект уже скачан, просто откройте PowerShell в его папке, содержащей `pyproject.toml`.

## 3. Установить Poetry и зависимости

Poetry устанавливается в отдельное локальное окружение `.poetry-tools`. Глобальная установка и активация окружения не нужны.

```powershell
py -3.11 -m venv .poetry-tools
.\.poetry-tools\Scripts\python.exe -m pip install "poetry>=2,<3"
$env:POETRY_VIRTUALENVS_IN_PROJECT = "true"
$pythonPath = py -3.11 -c "import sys; print(sys.executable)"
.\.poetry-tools\Scripts\poetry.exe env use $pythonPath
.\.poetry-tools\Scripts\poetry.exe install
```

Первичная установка требует доступа к интернету. Зависимости проекта устанавливаются из `poetry.lock` в `.venv`.

## 4. Построить сетку и открыть окно просмотра

Канал с изогнутыми стенками, экспериментальная линейная модель:

```powershell
.\.poetry-tools\Scripts\poetry.exe run mesh2d examples/channel.json --method ai --format vtk -o out/channel.vtk --plot out/channel.png --show
```

Классический метод для того же канала:

```powershell
.\.poetry-tools\Scripts\poetry.exe run mesh2d examples/channel.json --method tfi --format vtk -o out/channel_tfi.vtk --plot out/channel_tfi.png --show
```

Круг:

```powershell
.\.poetry-tools\Scripts\poetry.exe run mesh2d examples/circle.json --method radial --format vtk -o out/circle.vtk --plot out/circle.png --show
```

Пятиконечная звезда:

```powershell
.\.poetry-tools\Scripts\poetry.exe run mesh2d examples/star.json --method radial --format vtk -o out/star.vtk --plot out/star.png --show
```

Два эллипса со смещённым внутренним контуром:

```powershell
.\.poetry-tools\Scripts\poetry.exe run mesh2d examples/ellipse_ring.json --method radial --format vtk -o out/ellipse_ring.vtk --plot out/ellipse_ring.png --show
```

Четырёхугольное отверстие внутри эллипса:

```powershell
.\.poetry-tools\Scripts\poetry.exe run mesh2d examples/ellipse_quad.json --method radial --format vtk -o out/ellipse_quad.vtk --plot out/ellipse_quad.png --show
```

Окно Matplotlib позволяет приближать и перемещать изображение. Закройте его, чтобы команда завершилась. Для сохранения результата без окна уберите `--show`. PNG можно открыть обычным просмотрщиком изображений. Круг, звезда и вложенные контуры строятся геометрически, без ИИ.

## 5. Экспорт и изменение параметров

Для SU2:

```powershell
.\.poetry-tools\Scripts\poetry.exe run mesh2d examples/ellipse_quad.json --method radial --format su2 -o out/ellipse_quad.su2
```

Для словаря OpenFOAM:

```powershell
.\.poetry-tools\Scripts\poetry.exe run mesh2d examples/channel.json --format foam -o out/case/system/blockMeshDict
```

Последняя команда только создаёт словарь. Запуск `blockMesh`, `checkMesh` и расчётов требует отдельной установки OpenFOAM, например в WSL.

Изменяйте геометрию и число ячеек в JSON из папки `examples`, затем повторяйте команду. Для кольцевых областей `cells` задаёт количество ячеек по окружности и по толщине. `inner_center` смещает внутренний контур; `inner_axes` и `outer_axes` задают полуоси (для внутреннего прямоугольника — половины ширины и высоты).

Файлы VTK можно открыть в ParaView: File → Open → Apply, затем выбрать Surface With Edges. Результаты в `out` и локальные окружения исключены из Git.

## 6. Проверить установку

```powershell
.\.poetry-tools\Scripts\poetry.exe run python -m unittest discover -s tests -v
.\.poetry-tools\Scripts\poetry.exe run mesh2d --help
```

Если `py` не найден, проверьте установку Python и откройте новое окно терминала. Если команда не видит `pyproject.toml`, перейдите в папку проекта. Ошибка о перевёрнутых или вырожденных ячейках означает, что нужно изменить геометрию или параметры сетки.
