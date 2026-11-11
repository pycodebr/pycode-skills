"""PPTX mínimo, sem dependências: uma imagem por slide (o estado final da cena) e o texto nas notas do apresentador.

O arquivo segue o Office Open XML (ECMA-376) com mestre, layout e tema próprios. O design vira imagem; o texto
não fica editável como objeto (o texto da cena e as notas de fala vão para as notas de cada slide).
"""
from __future__ import annotations

import io
import zipfile
from pathlib import Path
from xml.sax.saxutils import escape

EMU_W, EMU_H = 12192000, 6858000
NS = ('xmlns:a="http://schemas.openxmlformats.org/drawingml/2006/main" '
      'xmlns:r="http://schemas.openxmlformats.org/officeDocument/2006/relationships" '
      'xmlns:p="http://schemas.openxmlformats.org/presentationml/2006/main"')
R = "http://schemas.openxmlformats.org/officeDocument/2006/relationships"
CORE = "http://schemas.openxmlformats.org/package/2006/relationships/metadata/core-properties"
XML = '<?xml version="1.0" encoding="UTF-8" standalone="yes"?>\n'

THEME = XML + f'''<a:theme {NS} name="pycode"><a:themeElements>
<a:clrScheme name="pycode"><a:dk1><a:srgbClr val="000000"/></a:dk1><a:lt1><a:srgbClr val="FFFFFF"/></a:lt1><a:dk2><a:srgbClr val="1F2937"/></a:dk2><a:lt2><a:srgbClr val="F3F4F6"/></a:lt2>
<a:accent1><a:srgbClr val="2563EB"/></a:accent1><a:accent2><a:srgbClr val="D97706"/></a:accent2><a:accent3><a:srgbClr val="059669"/></a:accent3><a:accent4><a:srgbClr val="7C3AED"/></a:accent4>
<a:accent5><a:srgbClr val="DC2626"/></a:accent5><a:accent6><a:srgbClr val="0891B2"/></a:accent6><a:hlink><a:srgbClr val="2563EB"/></a:hlink><a:folHlink><a:srgbClr val="7C3AED"/></a:folHlink></a:clrScheme>
<a:fontScheme name="pycode"><a:majorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:majorFont><a:minorFont><a:latin typeface="Arial"/><a:ea typeface=""/><a:cs typeface=""/></a:minorFont></a:fontScheme>
<a:fmtScheme name="pycode"><a:fillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:fillStyleLst>
<a:lnStyleLst><a:ln w="9525"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="19050"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln><a:ln w="28575"><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:ln></a:lnStyleLst>
<a:effectStyleLst><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle><a:effectStyle><a:effectLst/></a:effectStyle></a:effectStyleLst>
<a:bgFillStyleLst><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill><a:solidFill><a:schemeClr val="phClr"/></a:solidFill></a:bgFillStyleLst></a:fmtScheme>
</a:themeElements><a:objectDefaults/><a:extraClrSchemeLst/></a:theme>'''

EMPTY_TREE = ('<p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr>'
              '<p:grpSpPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="0" cy="0"/><a:chOff x="0" y="0"/><a:chExt cx="0" cy="0"/></a:xfrm></p:grpSpPr>{body}</p:spTree>')
CLRMAP = '<p:clrMap bg1="lt1" tx1="dk1" bg2="lt2" tx2="dk2" accent1="accent1" accent2="accent2" accent3="accent3" accent4="accent4" accent5="accent5" accent6="accent6" hlink="hlink" folHlink="folHlink"/>'
TXSTYLE = '<a:lvl1pPr><a:defRPr sz="1800"/></a:lvl1pPr>'


def _rels(items: list[tuple[str, str, str]]) -> str:
    rows = "".join(f'<Relationship Id="{rid}" Type="{kind if kind.startswith('http') else R + '/' + kind}" Target="{target}"/>'
                   for rid, kind, target in items)
    return XML + f'<Relationships xmlns="http://schemas.openxmlformats.org/package/2006/relationships">{rows}</Relationships>'


def _paragraphs(lines: list[str]) -> str:
    return "".join(f'<a:p><a:r><a:rPr lang="pt-BR" dirty="0"/><a:t>{escape(line)}</a:t></a:r></a:p>' for line in lines if line) or "<a:p/>"


def _slide(n: int, title: str) -> str:
    pic = (f'<p:pic><p:nvPicPr><p:cNvPr id="2" name="Cena {n}" descr="{escape(title, {chr(34): "&quot;"})}"/><p:cNvPicPr><a:picLocks noChangeAspect="1"/></p:cNvPicPr><p:nvPr/></p:nvPicPr>'
           f'<p:blipFill><a:blip r:embed="rId2"/><a:stretch><a:fillRect/></a:stretch></p:blipFill>'
           f'<p:spPr><a:xfrm><a:off x="0" y="0"/><a:ext cx="{EMU_W}" cy="{EMU_H}"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr></p:pic>')
    return XML + f'<p:sld {NS}><p:cSld><p:spTree><p:nvGrpSpPr><p:cNvPr id="1" name=""/><p:cNvGrpSpPr/><p:nvPr/></p:nvGrpSpPr><p:grpSpPr/>{pic}</p:spTree></p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sld>'


def _notes(lines: list[str]) -> str:
    body = (f'<p:sp><p:nvSpPr><p:cNvPr id="2" name="Notas"/><p:cNvSpPr><a:spLocks noGrp="1"/></p:cNvSpPr><p:nvPr><p:ph type="body" idx="1"/></p:nvPr></p:nvSpPr>'
            f'<p:spPr><a:xfrm><a:off x="685800" y="4343400"/><a:ext cx="5486400" cy="4114800"/></a:xfrm><a:prstGeom prst="rect"><a:avLst/></a:prstGeom></p:spPr>'
            f'<p:txBody><a:bodyPr/><a:lstStyle/>{_paragraphs(lines)}</p:txBody></p:sp>')
    return XML + f'<p:notes {NS}><p:cSld>{EMPTY_TREE.format(body=body)}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:notes>'


def write_pptx(slides: list[dict], out: Path, title: str = "", author: str = "", quality: int = 88) -> Path:
    """slides: [{"image": Path, "title": str, "notes": [linhas]}]."""
    from PIL import Image
    n = len(slides)
    files: dict[str, str | bytes] = {}
    ct = ['<Default Extension="rels" ContentType="application/vnd.openxmlformats-package.relationships+xml"/>',
          '<Default Extension="xml" ContentType="application/xml"/>', '<Default Extension="jpeg" ContentType="image/jpeg"/>',
          '<Override PartName="/ppt/presentation.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.presentation.main+xml"/>',
          '<Override PartName="/ppt/slideMasters/slideMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideMaster+xml"/>',
          '<Override PartName="/ppt/slideLayouts/slideLayout1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slideLayout+xml"/>',
          '<Override PartName="/ppt/notesMasters/notesMaster1.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesMaster+xml"/>',
          '<Override PartName="/ppt/theme/theme1.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
          '<Override PartName="/ppt/theme/theme2.xml" ContentType="application/vnd.openxmlformats-officedocument.theme+xml"/>',
          '<Override PartName="/docProps/core.xml" ContentType="application/vnd.openxmlformats-package.core-properties+xml"/>',
          '<Override PartName="/docProps/app.xml" ContentType="application/vnd.openxmlformats-officedocument.extended-properties+xml"/>']
    for i in range(1, n + 1):
        ct.append(f'<Override PartName="/ppt/slides/slide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.slide+xml"/>')
        ct.append(f'<Override PartName="/ppt/notesSlides/notesSlide{i}.xml" ContentType="application/vnd.openxmlformats-officedocument.presentationml.notesSlide+xml"/>')
    files["[Content_Types].xml"] = XML + '<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">' + "".join(ct) + "</Types>"
    files["_rels/.rels"] = _rels([("rId1", "officeDocument", "ppt/presentation.xml"),
                                   ("rId2", CORE, "docProps/core.xml"),
                                   ("rId3", "extended-properties", "docProps/app.xml")])
    files["docProps/core.xml"] = XML + ('<cp:coreProperties xmlns:cp="http://schemas.openxmlformats.org/package/2006/metadata/core-properties" '
                                        'xmlns:dc="http://purl.org/dc/elements/1.1/" xmlns:dcterms="http://purl.org/dc/terms/" '
                                        'xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance">'
                                        f'<dc:title>{escape(title)}</dc:title><dc:creator>{escape(author)}</dc:creator></cp:coreProperties>')
    files["docProps/app.xml"] = XML + ('<Properties xmlns="http://schemas.openxmlformats.org/officeDocument/2006/extended-properties">'
                                       f'<Application>pycode-aulas</Application><Slides>{n}</Slides><Notes>{n}</Notes></Properties>')
    pres_rels = [("rId1", "slideMaster", "slideMasters/slideMaster1.xml"), ("rId2", "theme", "theme/theme1.xml"),
                 ("rId3", "notesMaster", "notesMasters/notesMaster1.xml")]
    sld_ids = []
    for i in range(1, n + 1):
        pres_rels.append((f"rId{i + 3}", "slide", f"slides/slide{i}.xml"))
        sld_ids.append(f'<p:sldId id="{255 + i}" r:id="rId{i + 3}"/>')
    files["ppt/_rels/presentation.xml.rels"] = _rels(pres_rels)
    files["ppt/presentation.xml"] = XML + (f'<p:presentation {NS} saveSubsetFonts="1"><p:sldMasterIdLst><p:sldMasterId id="2147483648" r:id="rId1"/></p:sldMasterIdLst>'
                                           f'<p:notesMasterIdLst><p:notesMasterId r:id="rId3"/></p:notesMasterIdLst><p:sldIdLst>{"".join(sld_ids)}</p:sldIdLst>'
                                           f'<p:sldSz cx="{EMU_W}" cy="{EMU_H}"/><p:notesSz cx="6858000" cy="9144000"/></p:presentation>')
    files["ppt/theme/theme1.xml"] = THEME
    files["ppt/theme/theme2.xml"] = THEME
    files["ppt/slideMasters/slideMaster1.xml"] = XML + (f'<p:sldMaster {NS}><p:cSld><p:bg><p:bgPr><a:solidFill><a:srgbClr val="000000"/></a:solidFill><a:effectLst/></p:bgPr></p:bg>'
                                                       f'{EMPTY_TREE.format(body="")}</p:cSld>{CLRMAP}<p:sldLayoutIdLst><p:sldLayoutId id="2147483649" r:id="rId1"/></p:sldLayoutIdLst>'
                                                       f'<p:txStyles><p:titleStyle>{TXSTYLE}</p:titleStyle><p:bodyStyle>{TXSTYLE}</p:bodyStyle><p:otherStyle>{TXSTYLE}</p:otherStyle></p:txStyles></p:sldMaster>')
    files["ppt/slideMasters/_rels/slideMaster1.xml.rels"] = _rels([("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml"), ("rId2", "theme", "../theme/theme1.xml")])
    files["ppt/slideLayouts/slideLayout1.xml"] = XML + f'<p:sldLayout {NS} type="blank" preserve="1"><p:cSld name="Imagem">{EMPTY_TREE.format(body="")}</p:cSld><p:clrMapOvr><a:masterClrMapping/></p:clrMapOvr></p:sldLayout>'
    files["ppt/slideLayouts/_rels/slideLayout1.xml.rels"] = _rels([("rId1", "slideMaster", "../slideMasters/slideMaster1.xml")])
    files["ppt/notesMasters/notesMaster1.xml"] = XML + f'<p:notesMaster {NS}><p:cSld>{EMPTY_TREE.format(body="")}</p:cSld>{CLRMAP}<p:notesStyle>{TXSTYLE}</p:notesStyle></p:notesMaster>'
    files["ppt/notesMasters/_rels/notesMaster1.xml.rels"] = _rels([("rId1", "theme", "../theme/theme2.xml")])
    for i, s in enumerate(slides, start=1):
        im = Image.open(s["image"]).convert("RGB")
        buf = io.BytesIO()
        im.save(buf, "JPEG", quality=quality, optimize=True)
        files[f"ppt/media/image{i}.jpeg"] = buf.getvalue()
        files[f"ppt/slides/slide{i}.xml"] = _slide(i, s.get("title", ""))
        files[f"ppt/slides/_rels/slide{i}.xml.rels"] = _rels([("rId1", "slideLayout", "../slideLayouts/slideLayout1.xml"),
                                                               ("rId2", "image", f"../media/image{i}.jpeg"),
                                                               ("rId3", "notesSlide", f"../notesSlides/notesSlide{i}.xml")])
        files[f"ppt/notesSlides/notesSlide{i}.xml"] = _notes(s.get("notes") or [])
        files[f"ppt/notesSlides/_rels/notesSlide{i}.xml.rels"] = _rels([("rId1", "notesMaster", "../notesMasters/notesMaster1.xml"),
                                                                       ("rId2", "slide", f"../slides/slide{i}.xml")])
    out.parent.mkdir(parents=True, exist_ok=True)
    with zipfile.ZipFile(out, "w", zipfile.ZIP_DEFLATED) as z:
        z.writestr("[Content_Types].xml", files.pop("[Content_Types].xml"))
        for name, data in files.items():
            z.writestr(name, data)
    return out
