# 스킨 업로드 양식

스킨은 `skin.json`과 PNG로 만들고, 필요하면 글꼴과 3D 월드 페이지를 더합니다. 자동 검사를 통과하면 바로 목록에 공개됩니다. 3D 월드 페이지가 있는 스킨만 관리자 검토 후 공개됩니다.

## 폴더 구성

```text
my-skin/
├─ skin.json     (필수)
└─ sky.png       (theme에서 쓰는 이미지만)
```

넣을 수 있는 파일은 `.json`, `.png`, `.txt`, `.md`, `.html`, `.ttf`, `.otf`이고, 전체 64MB까지입니다.

## skin.json

```json
{
  "id": "my-skin",
  "name": "내 스킨",
  "version": "1.0.0",
  "description": "내 스킨 설명",
  "colors": { "Bg": "#06141A", "Panel": "#DE0B1F26", "Ink": "#E8FFF6", "Mint": "#6CF2C2" },
  "theme": { "background": "sky.png", "backgroundOpacity": 0.6, "stars": 160 }
}
```

| 항목 | 필수 | 규칙 |
|---|---|---|
| `id` | 예 | 영문 소문자·숫자로 시작하고 소문자·숫자·`.`·`_`·`-`만 씁니다. 64자까지이며 `.`으로 끝날 수 없습니다. `default`, `midnight`, `space`, `voxel`은 쓸 수 없습니다. |
| `name` | 예 | 목록에 보이는 이름, 64자까지 |
| `version` | 예 | 영문·숫자로 시작하고 영문·숫자·`.`·`-`만 씁니다. 32자까지이며 `1.0.0` 형식을 권장합니다. |
| `description` | 아니요 | 목록에 200자까지 표시 |
| `colors` | 아니요 | 아래 색 토큰. 쓰지 않은 색은 기본 스킨을 따릅니다. |
| `theme` | 아니요 | 아래 시각 효과 |

색상만 바꾸는 예시는 [samples/midnight-color](../samples/midnight-color/skin.json), 시각 효과까지 쓰는 예시는 [samples/space-voyage](../samples/space-voyage/skin.json)에 있습니다.

## 색 토큰

값은 `#RRGGBB` 또는 `#AARRGGBB`입니다. 목록에 없는 이름이 있으면 거부됩니다.

| 토큰 | 쓰임 |
|---|---|
| `Bg`, `OverlayBackdrop`, `ModalBackdrop` | 배경, 오버레이 배경, 모달 뒤 배경 |
| `Panel`, `Edge` | 패널 면과 테두리 |
| `Ink`, `Muted` | 기본 글자, 보조 글자 |
| `Mint`, `OnAccent` | 강조색, 강조색 위 글자 |
| `Danger`, `DangerSoft` | 오류와 삭제 |
| `Input`, `Selected`, `Hover` | 입력란, 선택, 마우스 올림 |
| `ScheduleNow` | 곧 끝나는 현재 일정 |
| `CalendarSunday`, `CalendarSaturday` | 달력의 일요일, 토요일 |

## theme

| 항목 | 범위 | 설명 |
|---|---|---|
| `background` | PNG 이름 | 배경 이미지 |
| `backgroundOpacity` | 0–1 | 배경 이미지 불투명도 |
| `stars` | 0–500 | 별 개수 |
| `nebulaSpeed` | 0–8 | 성운 속도, 0이면 끔 |
| `nebulaBrightness` | 0–1 | 성운 밝기 |
| `frame` | PNG 이름 | 위젯 틀(9-slice) 이미지 |
| `frameSlice` | 1–128 | 틀 모서리 크기. `frame`을 쓰면 필수이고, 이미지 가로·세로는 이 값의 2배보다 커야 합니다. |
| `framePadding` | 0–32 | 틀 안쪽 여백 |
| `panelMarkLength` | 0–32 | 패널 모서리 표시 길이 |
| `panelCornerRadius` | 0–24 | 패널 모서리 반경 |
| `tabCornerRadius` | 0–24 | 탭 막대 모서리 반경 |
| `voyage` | true/false | 우주 항해 배경 |
| `hudWidgets` | true/false | 위젯을 HUD 형태로 표시 |
| `world` | `{ "page": "world.html", "scenes": [...] }` | 스킨에 포함한 HTML 페이지를 실시간 배경으로 띄웁니다. `scenes`는 페이지에 그대로 전달되며 배경을 누를 때마다 다음으로 넘어갑니다. |
| `fonts` | `{ "body": { "file", "family" }, "heading": {...} }` | 스킨에 포함한 글꼴. `file`은 `.ttf`·`.otf` 이름, `family`는 글꼴 안의 이름입니다. |
| `hudStyle` | `tactical`, `soft` | HUD 위젯 모양. `soft`는 둥근 패널 형태입니다. `hudWidgets`와 함께 씁니다. |
| `options` | 목록 | 설정에 나타날 선택 항목. `id`(소문자·숫자·`-`, 32자까지), `name`이 필수이고 `description`, `default`를 쓸 수 있습니다. |

이미지는 스킨 폴더 바로 아래의 PNG만 씁니다. 이름은 영문 소문자·숫자·`_`·`-`이고, 한 변은 8192픽셀까지입니다.

## 3D 월드 페이지

페이지는 파일 하나이고 1.9MB까지입니다. 인터넷, 외부 파일, 사용자 기록에 접근할 수 없습니다. 앱이 잠금을 강제합니다.

- 받는 메시지: `chrome.webview`의 `message` 이벤트로 `{ scenes }`, `{ weather }`(`clear`, `partly`, `cloud`, `rain`, `snow`, `fog`), `{ visible }`, `{ next: true }`
- 보내는 메시지: 시작할 때 `{ type: "loaded" }`, 준비되면 `{ type: "ready" }`, 실패하면 `{ type: "failed", message }`
- 시각은 페이지에서 `Date`로 읽습니다.

월드 페이지는 코드이므로 이런 스킨은 바로 공개되지 않고 관리자 검토를 거칩니다.

## 미리 확인

폴더를 `%LOCALAPPDATA%\MaterialStone\DailyDock\skins\` 아래에 넣고 Facet 설정의 스킨 목록에서 선택합니다.

## 올리기

1. Facet 설정 → 플러그인 → **스킨·플러그인 받기** → **올리기**에서 스킨 폴더를 고릅니다.
2. zip이 만들어지고 [제출 양식](https://github.com/YouHyunwoo/facet-registry/issues/new?template=submit.yml)이 열립니다. GitHub에 로그인합니다.
3. zip 하나를 양식에 끌어다 놓고 제출합니다.

검사를 통과하면 이슈가 닫히며 공개됩니다. 실패하면 이슈 댓글의 실행 기록에서 이유를 볼 수 있습니다. zip을 직접 만든다면 `skin.json`이 zip의 맨 위에 있어야 합니다.

## 업데이트

`version`을 올려 같은 방법으로 제출합니다. 같은 `id`는 처음 올린 계정만 갱신할 수 있고, 이미 공개한 버전은 다시 올릴 수 없습니다.
