# 플러그인 업로드 양식

플러그인은 .NET 10 WPF 클래스 라이브러리입니다. 사용자의 PC에서 앱과 같은 권한으로 실행되므로, 자동 검사 후 **관리자 승인을 받아야 공개됩니다.**

## 프로젝트

`Facet.Plugins.dll`은 설치된 Facet의 release 폴더에 있습니다. 참조만 하고 패키지에는 넣지 않습니다.

```xml
<Project Sdk="Microsoft.NET.Sdk">
  <PropertyGroup>
    <TargetFramework>net10.0-windows10.0.19041.0</TargetFramework>
    <UseWPF>true</UseWPF>
    <ImplicitUsings>enable</ImplicitUsings>
    <Nullable>enable</Nullable>
  </PropertyGroup>
  <ItemGroup>
    <Reference Include="Facet.Plugins">
      <HintPath>경로\Facet.Plugins.dll</HintPath>
      <Private>false</Private>
    </Reference>
    <None Include="plugin.json" CopyToOutputDirectory="PreserveNewest" />
  </ItemGroup>
</Project>
```

```csharp
using System.Windows.Controls;
using Facet.Plugins;

public sealed class MyPlugin : IFacetPlugin
{
    public void Register(IWidgetRegistry registry) =>
        registry.AddWidget(new WidgetDescriptor("hello", "인사", _ => new TextBlock { Text = "안녕하세요" }));
}
```

UI는 코드로 만드세요. 별도 load context에서는 XAML의 pack URI 리소스가 해석되지 않을 수 있습니다. 오래 걸리는 작업은 백그라운드에서 처리하세요.

## 폴더 구성

`dotnet publish`의 결과 폴더를 올립니다.

```text
my-plugin/
├─ plugin.json   (필수)
├─ MyPlugin.dll  (필수)
└─ 의존 DLL과 도구 파일
```

전체 1GB, 파일 5000개까지입니다.

## plugin.json

```json
{
  "id": "my.plugin",
  "name": "내 플러그인",
  "version": "1.0.0",
  "description": "인사를 표시하는 위젯",
  "assembly": "MyPlugin.dll"
}
```

| 항목 | 필수 | 규칙 |
|---|---|---|
| `id` | 예 | 영문 소문자·숫자로 시작하고 소문자·숫자·`.`·`_`·`-`만 씁니다. 64자까지이며 `.`으로 끝날 수 없습니다. |
| `name` | 예 | 목록에 보이는 이름, 64자까지 |
| `version` | 예 | 영문·숫자로 시작하고 영문·숫자·`.`·`-`만 씁니다. 32자까지이며 `1.0.0` 형식을 권장합니다. |
| `description` | 아니요 | 목록에 200자까지 표시 |
| `assembly` | 예 | 패키지 맨 위에 있는 DLL 파일 이름. 경로는 쓸 수 없습니다. |

`id`는 저장 데이터의 키이므로 공개한 뒤에는 바꾸지 마세요.

## 미리 확인

폴더를 `%LOCALAPPDATA%\MaterialStone\DailyDock\plugins\` 아래에 넣고 Facet 설정 → 플러그인에서 켭니다. 위젯은 탭의 위젯 편집에서 배치합니다.

## 올리기

1. Facet 설정 → 플러그인 → **스킨·플러그인 받기** → **올리기**에서 publish 폴더를 고릅니다. `.pdb` 파일은 자동으로 빠집니다.
2. zip이 만들어지고 [제출 양식](https://github.com/YouHyunwoo/facet-registry/issues/new?template=submit.yml)이 열립니다. GitHub에 로그인합니다.
3. zip 하나를 양식에 끌어다 놓고 제출합니다.
4. 자동 검사를 통과하면 PR이 만들어지고 관리자 검토를 기다립니다. 병합되면 목록에 공개됩니다.

자동 검사는 패키지의 형식만 확인하며 코드를 실행하지 않습니다. 실패하면 이슈 댓글의 실행 기록에서 이유를 볼 수 있습니다. zip을 직접 만든다면 `plugin.json`이 zip의 맨 위에 있어야 합니다.

## 승인을 빠르게 받으려면

제출 이슈에 다음을 함께 적어 주세요.

- 소스 코드 저장소 링크
- 네트워크 접속, 파일 접근, 외부 프로그램 실행 여부와 이유
- 포함한 외부 DLL과 실행 파일의 출처

승인은 코드 안전을 보증하지 않습니다. 플러그인은 샌드박스 없이 실행되므로 사용자의 기록을 읽거나 파일을 바꾸는 코드는 넣지 마세요.

## 업데이트

`version`을 올려 같은 방법으로 제출합니다. 업데이트도 다시 승인을 받습니다. 같은 `id`는 처음 올린 계정만 갱신할 수 있고, 이미 공개한 버전은 다시 올릴 수 없습니다.
