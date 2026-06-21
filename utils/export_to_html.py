import os
import re
import sys
import argparse

HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="zh-CN">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>{title}</title>
    <link href="https://fonts.googleapis.com/css2?family=LXGW+Wen+Kai:wght@400;700&family=Ma+Shan+Zheng&family=Nunito:wght@400;600;700&display=swap" rel="stylesheet">
    <style>
        :root {{
            --bg-color: #f7f5ee; /* Warm cream paper background */
            --card-bg: #ffffff;
            --text-primary: #1a1a1a; /* Ink black */
            --text-secondary: #7f8c8d; /* Grey for pinyin and subtitle */
            --accent-red: #c0392b; /* Crimson red */
            --accent-ochre: #d35400;
            --border-color: #e5e0d3;
            --shadow: 0 10px 30px rgba(0,0,0,0.06);
        }}

        body {{
            font-family: 'Nunito', sans-serif;
            background-color: var(--bg-color);
            color: var(--text-primary);
            margin: 0;
            padding: 0;
            line-height: 1.6;
            height: 100vh;
            overflow: hidden; /* Prevent scrolling on desktop/iPad viewport */
        }}

        /* Sticky Top Navigation */
        .sticky-nav {{
            position: sticky;
            top: 0;
            z-index: 1000;
            background: rgba(247, 245, 238, 0.95);
            backdrop-filter: blur(8px);
            border-bottom: 1px solid var(--border-color);
            display: flex;
            flex-direction: column;
            align-items: center;
            padding: 12px 24px;
            box-sizing: border-box;
            gap: 12px;
            height: auto;
        }}

        .nav-back-btn {{
            position: absolute;
            left: 24px;
            top: 20px;
            display: flex;
            align-items: center;
            gap: 8px;
            color: var(--text-secondary);
            text-decoration: none;
            font-weight: 600;
            font-size: 0.95rem;
            transition: color 0.2s;
        }}

        .nav-back-btn:hover {{
            color: var(--accent-red);
        }}

        .nav-title {{
            font-family: 'LXGW Wen Kai', serif;
            font-weight: 700;
            font-size: 1.35rem;
            color: var(--text-primary);
        }}

        .nav-pinyin {{
            font-family: 'Nunito', sans-serif;
            font-weight: 400;
            font-size: 1rem;
            color: var(--text-secondary);
            margin-left: 6px;
        }}

        /* Language Toggle pill selector */
        .toggle-container {{
            display: flex;
            background: #e8e4d9;
            padding: 3px;
            border-radius: 30px;
            border: 1px solid #dcd8cc;
        }}

        .toggle-btn {{
            background: transparent;
            border: none;
            outline: none;
            cursor: pointer;
            padding: 6px 14px;
            border-radius: 20px;
            font-family: 'Nunito', sans-serif;
            font-size: 0.85rem;
            font-weight: 600;
            color: var(--text-secondary);
            transition: all 0.2s ease;
        }}

        .toggle-btn.active {{
            background: #ffffff;
            color: var(--text-primary);
            box-shadow: 0 2px 6px rgba(0,0,0,0.08);
        }}

        .nav-controls-group {{
            display: flex;
            align-items: center;
            gap: 20px;
        }}

        /* Bottom Page Navigation Controls */
        .bottom-controls {{
            position: fixed;
            bottom: 0;
            left: 0;
            width: 100%;
            display: flex;
            justify-content: center;
            gap: 20px;
            padding: 12px 24px;
            background: rgba(247, 245, 238, 0.95);
            backdrop-filter: blur(8px);
            border-top: 1px solid var(--border-color);
            box-sizing: border-box;
            z-index: 1000;
        }}

        .bottom-controls .control-btn {{
            background: #ffffff;
            border: 1px solid var(--border-color);
            width: 44px;
            height: 44px;
            border-radius: 50%;
            cursor: pointer;
            display: flex;
            align-items: center;
            justify-content: center;
            box-shadow: 0 2px 8px rgba(0,0,0,0.05);
            color: var(--text-primary);
            transition: all 0.25s ease;
        }}

        .bottom-controls .control-btn:hover {{
            background: var(--bg-color);
            color: var(--accent-red);
            transform: scale(1.05);
        }}

        .bottom-controls .control-btn:disabled {{
            opacity: 0.3;
            cursor: not-allowed;
            transform: none;
        }}

        /* Book Layout Container - fits viewport exactly */
        .book-container {{
            display: flex;
            justify-content: center;
            align-items: center;
            perspective: 2000px;
            height: calc(100vh - 200px); /* Adjust for nav and bottom controls */
            margin: 10px auto;
            width: 100%;
            max-width: 1200px;
            box-sizing: border-box;
            position: relative;
        }}

        .book {{
            position: relative;
            height: 92%;
            aspect-ratio: 1.42 / 1; /* Classic physical book aspect ratio */
            max-width: 90vw;
            transition: transform 0.6s cubic-bezier(0.25, 1, 0.5, 1);
            transform-style: preserve-3d;
        }}

        /* Spine Crease shadow overlay when book is open */
        .book.open::after {{
            content: '';
            position: absolute;
            width: 10px;
            height: 100%;
            left: 50%;
            top: 0;
            transform: translateX(-50%);
            background: linear-gradient(to right, 
                rgba(0,0,0,0.03) 0%, 
                rgba(0,0,0,0.01) 30%, 
                rgba(0,0,0,0.05) 50%, 
                rgba(0,0,0,0.01) 70%, 
                rgba(0,0,0,0.03) 100%
            );
            z-index: 105;
            pointer-events: none;
            mix-blend-mode: multiply;
        }}

        /* Paper sheet / leaf */
        .paper {{
            position: absolute;
            width: 50%;
            height: 100%;
            top: 0;
            right: 0;
            transform-origin: left center;
            transform-style: preserve-3d;
            transition: transform 0.55s cubic-bezier(0.25, 1, 0.5, 1);
            cursor: pointer;
            user-select: none;
        }}

        .front,
        .back {{
            position: absolute;
            width: 100%;
            height: 100%;
            top: 0;
            left: 0;
            background-color: #ffffff;
            box-sizing: border-box;
            padding: 35px;
            backface-visibility: hidden;
            overflow-y: auto;
            border: 1px solid var(--border-color);
        }}

        .front {{
            border-radius: 0 12px 12px 0;
            box-shadow: inset -12px 0 20px rgba(0,0,0,0.03), 3px 6px 15px rgba(0,0,0,0.04);
            z-index: 2;
        }}

        .back {{
            border-radius: 12px 0 0 12px;
            box-shadow: inset 12px 0 20px rgba(0,0,0,0.03), -3px 6px 15px rgba(0,0,0,0.04);
            transform: rotateY(180deg);
        }}

        /* Flipped state */
        .paper.flipped {{
            transform: rotateY(-180deg);
        }}

        /* Cover Page Full-bleed Layout */
        .cover-front {{
            padding: 0 !important;
            overflow: hidden !important;
            position: relative;
            background: #f7f5ee;
        }}

        .cover-bg {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            object-fit: cover;
            z-index: 1;
        }}

        .cover-overlay {{
            position: absolute;
            top: 0;
            left: 0;
            width: 100%;
            height: 100%;
            z-index: 2;
            display: flex;
            flex-direction: column;
            justify-content: flex-start;
            align-items: center;
            padding: 50px 30px;
            box-sizing: border-box;
            background: linear-gradient(to bottom, 
                rgba(247, 245, 238, 0.85) 0%, 
                rgba(247, 245, 238, 0.4) 40%, 
                rgba(247, 245, 238, 0) 80%
            );
        }}

        .cover-title-group {{
            display: flex;
            flex-direction: column;
            align-items: center;
            gap: 4px;
            text-align: center;
            width: 100%;
        }}

        .cover-pinyin {{
            font-family: 'Nunito', sans-serif;
            font-size: 1.1rem;
            font-weight: 700;
            color: #5d6d7e;
            text-shadow: 0 1px 3px rgba(255, 255, 255, 0.95);
            margin: 0;
            letter-spacing: 1px;
            line-height: 1.2;
        }}

        .cover-title {{
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 3.8rem;
            color: #1a1a1a; /* Calligraphic ink black */
            margin: 0;
            font-weight: normal;
            text-shadow: 0 2px 5px rgba(255, 255, 255, 0.9);
            letter-spacing: 4px;
        }}

        .cover-translation {{
            font-family: 'Nunito', sans-serif;
            font-size: 1.1rem;
            font-weight: 600;
            color: #555555;
            text-shadow: 0 1px 4px rgba(255, 255, 255, 0.95);
            margin: 0;
            font-style: italic;
            line-height: 1.3;
        }}

        /* Back Cover Style */
        .back-cover-content {{
            height: 100%;
            width: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            align-items: center;
            text-align: center;
            {back_cover_style}
            position: relative;
            box-sizing: border-box;
        }}

        .traditional-seal {{
            font-family: 'Ma Shan Zheng', cursive; /* Stamp/seal script */
            font-weight: normal;
            font-size: 1.5rem;
            border: 2px solid var(--accent-red);
            color: var(--accent-red);
            padding: 4px 10px;
            margin-top: 25px;
            letter-spacing: 2px;
            border-radius: 4px;
            transform: rotate(-3deg);
            background-color: transparent;
        }}

        /* Content Pages Layout */
        .image-content {{
            width: 100%;
            height: 100%;
            display: flex;
            align-items: center;
            justify-content: center;
        }}

        .image-content img {{
            max-width: 100%;
            max-height: 100%;
            object-fit: contain;
            border-radius: 8px;
            box-shadow: 0 3px 10px rgba(0,0,0,0.03);
            border: 1px solid var(--border-color);
        }}

        /* Selective Full-bleed watercolor styles for left story pages (p1-p6 back) */
        .paper:not(#p7):not(#p8) .back {{
            padding: 0 !important;
            border: none !important;
            border-radius: 0 !important;
            overflow: hidden !important;
            box-shadow: none !important;
        }}

        /* Double-page spread styles */
        .spread-left {{
            background-size: 200% auto !important;
            background-position: left center !important;
            background-repeat: no-repeat !important;
        }}

        .spread-right {{
            background-size: 200% auto !important;
            background-position: right center !important;
            background-repeat: no-repeat !important;
            position: relative;
        }}

        /* Clean full-bleed layout for right story pages (p2-p7 front) */
        .paper:not(#p1):not(#p8) .front {{
            border: none !important;
            border-radius: 0 !important;
            box-shadow: none !important;
            padding: 0 !important;
        }}

        /* Story Text Overlays on top of the right spread */
        .story-overlay {{
            position: absolute;
            left: 0;
            width: 100%;
            box-sizing: border-box;
            z-index: 10;
        }}

        .story-overlay.pos-bottom {{
            bottom: 0;
            padding: 50px 32px 30px 32px;
            background: linear-gradient(to top, 
                rgba(247, 245, 238, 0.98) 0%, 
                rgba(247, 245, 238, 0.85) 65%, 
                rgba(247, 245, 238, 0) 100%
            );
        }}

        .story-overlay.pos-top {{
            top: 0;
            padding: 50px 32px 50px 32px;
            background: linear-gradient(to bottom, 
                rgba(247, 245, 238, 0.98) 0%, 
                rgba(247, 245, 238, 0.85) 65%, 
                rgba(247, 245, 238, 0) 100%
            );
        }}

        .paper:not(#p1):not(#p8) .text-content {{
            height: auto !important;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 0 !important; /* Managed by story-overlay */
            box-sizing: border-box;
        }}

        .text-content {{
            height: 100%;
            display: flex;
            flex-direction: column;
            justify-content: center;
            padding: 10px;
        }}

        .beat-label {{
            display: none !important; /* Completely hide section labels on story pages */
        }}

        .lang-en {{
            font-size: 1.15rem;
            font-weight: 500;
            color: #2c3e50;
            line-height: 1.65;
            font-family: 'Nunito', sans-serif;
            margin-bottom: 28px; /* Slightly more space before bilingual block */
        }}

        .story-bilingual {{
            display: flex;
            flex-direction: column;
            gap: 36px; /* Clear paragraph spacing */
        }}

        .story-paragraph {{
            display: flex;
            flex-wrap: wrap;
            row-gap: 12px;      /* Vertical spacing between wrapped lines of character+pinyin */
            column-gap: 6px;    /* Horizontal spacing between phrases */
        }}

        /* Bilingual Display Styles */
        .sentence-pair {{
            display: inline-flex;
            flex-direction: column;
            align-items: center;
            margin-bottom: 0;
            white-space: nowrap;
        }}

        .lang-cn {{
            font-size: 1.45rem;
            font-weight: 700;
            color: #1a1a1a; /* Chinese is bold, dark ink black */
            font-family: 'LXGW Wen Kai', serif; /* Modern serif Chinese font */
            line-height: 1.35;
            text-align: center;
        }}

        .lang-py {{
            font-size: 0.9rem;
            color: #7f8c8d; /* Noticeably smaller size and soft gray pinyin */
            font-style: normal;
            font-family: 'Nunito', sans-serif;
            line-height: 1.2;
            font-weight: 400;
            text-align: center;
        }}

        /* Final calligraphic idiom styling */
        #p7 .story-bilingual .story-paragraph:last-child {{
            justify-content: center;
            width: 100%;
            margin-top: 14px;
        }}

        #p7 .story-bilingual .story-paragraph:last-child .lang-cn {{
            font-family: 'Ma Shan Zheng', cursive;
            font-size: 3.2rem; /* Larger calligraphic style */
            font-weight: normal;
            color: var(--accent-red);
            line-height: 1.2;
            margin-top: 6px;
        }}

        #p7 .story-bilingual .story-paragraph:last-child .lang-py {{
            font-size: 1.2rem;
            color: var(--text-secondary);
        }}

        /* Table and Idiom page styles */
        h2 {{
            font-family: 'LXGW Wen Kai', serif;
            color: #2c3e50;
            font-size: 1.3rem;
            margin-top: 0;
            margin-bottom: 10px;
            border-bottom: 1px solid var(--border-color);
            padding-bottom: 6px;
        }}

        table {{
            width: 100%;
            border-collapse: collapse;
            margin: 10px 0;
            font-size: 0.88rem;
            font-family: 'Nunito', sans-serif;
        }}

        th, td {{
            padding: 8px 10px;
            text-align: left;
            border-bottom: 1px solid var(--border-color);
        }}

        th {{
            background-color: #fcfcfc;
            font-weight: 600;
        }}

        .idiom-table td:first-child {{
            font-weight: bold;
            color: var(--accent-red);
            width: 32%;
        }}

        /* Editorial Idiom details grid */
        .idiom-details-grid {{
            display: grid;
            grid-template-columns: 1fr 1fr;
            gap: 8px 16px;
            margin: 10px 0 15px 0;
        }}

        .idiom-detail-item {{
            display: flex;
            flex-direction: column;
            gap: 2px;
        }}

        .idiom-detail-label {{
            font-family: 'Nunito', sans-serif;
            font-size: 0.75rem;
            text-transform: uppercase;
            letter-spacing: 1.5px;
            font-weight: 700;
            color: #7f8c8d;
        }}

        .idiom-detail-value {{
            font-size: 0.95rem;
            color: var(--text-primary);
            font-weight: 500;
        }}

        .idiom-detail-value.char-value {{
            font-family: 'LXGW Wen Kai', serif;
            font-size: 1.35rem;
            font-weight: 700;
        }}

        /* Callout Card Block for Examples */
        .example-quote-container {{
            position: relative;
            background: #fdfbf7;
            border: 1px solid rgba(211, 84, 0, 0.12);
            padding: 14px 16px 14px 20px;
            border-radius: 12px;
            margin-top: 12px;
            box-sizing: border-box;
        }}

        .quote-mark {{
            position: absolute;
            left: 8px;
            top: -2px;
            font-size: 2.8rem;
            font-family: 'Ma Shan Zheng', cursive;
            color: rgba(211, 84, 0, 0.12);
            line-height: 1;
            user-select: none;
        }}

        .example-quote-label {{
            font-size: 0.8rem;
            font-weight: 700;
            color: var(--accent-ochre);
            text-transform: uppercase;
            letter-spacing: 1px;
            margin-bottom: 6px;
            display: block;
        }}

        /* Timeline Layout for Story Spine */
        .timeline {{
            position: relative;
            padding-left: 30px;
            margin: 15px 0;
        }}

        .timeline::before {{
            content: '';
            position: absolute;
            left: 9px;
            top: 10px;
            bottom: 10px;
            width: 2px;
            background: var(--border-color);
        }}

        .timeline-item {{
            position: relative;
            margin-bottom: 12px;
        }}

        .timeline-item:last-child {{
            margin-bottom: 0;
        }}

        .timeline-badge {{
            position: absolute;
            left: -30px;
            top: 2px;
            width: 20px;
            height: 20px;
            border-radius: 50%;
            background: #e8e4d9;
            color: var(--text-primary);
            display: flex;
            align-items: center;
            justify-content: center;
            font-size: 0.75rem;
            font-weight: 700;
            border: 2px solid var(--card-bg);
            box-sizing: border-box;
            z-index: 2;
        }}

        .timeline-content strong {{
            font-family: 'LXGW Wen Kai', serif;
            color: #2c3e50;
            font-size: 0.98rem;
            font-weight: 700;
        }}

        .timeline-content p {{
            margin: 2px 0 0 0;
            font-size: 0.88rem;
            color: var(--text-primary);
            line-height: 1.4;
            font-weight: 500;
        }}

        /* Floating controls removed since they are moved to fixed bottom controls */

        /* Responsive Styles for Mobile */
        @media (max-width: 768px) {{
            body {{
                height: auto;
                overflow: auto; /* Allow scrolling on phone */
            }}
            
            .sticky-nav {{
                padding: 15px 15px;
                flex-direction: column;
                gap: 12px;
                height: auto;
                position: static; /* Disable sticky on mobile for scroll layout */
            }}
            
            .nav-back-btn {{
                position: static;
                margin-bottom: 4px;
            }}
            
            .nav-title {{
                font-size: 1.15rem;
                text-align: center;
            }}
            
            .nav-pinyin {{
                font-size: 0.85rem;
                display: block; /* Wrap pinyin on mobile */
                margin-left: 0;
                margin-top: 4px;
            }}
            
            .nav-controls-group {{
                flex-wrap: wrap;
                justify-content: center;
                gap: 12px;
                width: 100%;
            }}

            .bottom-controls {{
                display: none; /* Hide bottom controls on mobile scroll layout */
            }}

            .paper:not(#p7):not(#p8) .back {{
                height: 380px !important; /* Give story images a solid height on mobile scroll view */
                position: relative !important;
            }}

            .spread-left {{
                background-size: cover !important;
                background-position: center !important;
            }}

            .spread-right {{
                background-image: none !important;
                background-color: #ffffff !important;
            }}

            .story-overlay {{
                position: static !important;
                background: none !important;
                padding: 0 !important;
            }}

            .book-container {{
                perspective: none;
                height: auto;
                margin: 20px auto;
                padding: 0 15px;
            }}

            .book {{
                width: 100%;
                height: auto;
                transform: none !important;
                transform-style: flat;
                max-width: 100%;
                aspect-ratio: auto;
            }}

            .book.open::after {{
                display: none;
            }}

            .paper {{
                position: static;
                width: 100% !important;
                height: auto !important;
                transform: none !important;
                cursor: default;
                display: block;
                margin-bottom: 25px;
            }}

            .front,
            .back {{
                position: relative;
                width: 100% !important;
                height: auto !important;
                transform: none !important;
                backface-visibility: visible;
                box-shadow: 0 3px 10px rgba(0,0,0,0.03);
                border-radius: 12px;
                padding: 20px;
                border: 1px solid var(--border-color);
                margin-bottom: 12px;
                overflow-y: visible;
            }}

            .back {{
                margin-bottom: 0;
            }}

            .cover-front {{
                height: 480px !important;
                position: relative !important;
            }}
        }}
    </style>
</head>
<body>

    <!-- Sticky Navigation -->
    <nav class="sticky-nav">
        <a href="../" class="nav-back-btn">
            <svg width="18" height="18" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
            <span>Library</span>
        </a>

        <div class="nav-title-container">
            <span class="nav-title">{title} <span class="nav-pinyin">({idiom_py})</span></span>
        </div>
        <div class="nav-controls-group">
            <div class="toggle-container">
                <button class="toggle-btn" data-mode="english" onclick="setLanguageMode('english')">English</button>
                <button class="toggle-btn" data-mode="chinese" onclick="setLanguageMode('chinese')">中文</button>
                <button class="toggle-btn" data-mode="chinese-pinyin" onclick="setLanguageMode('chinese-pinyin')">中文 + 拼音</button>
            </div>
        </div>
    </nav>

    <!-- 3D Book Container -->
    <div class="book-container">

        <div class="book" id="book">
            <!-- Leaf 1: Cover / Beat 1 Image -->
            <div class="paper" id="p1">
                <div class="front cover-front">
                    <img class="cover-bg" src="{cover_image_path}" alt="Book Cover">
                    <div class="cover-overlay">
                        <div class="cover-title-group">
                            <div class="cover-pinyin">{cover_pinyin}</div>
                            <h1 class="cover-title">{title}</h1>
                            <div class="cover-translation">{cover_translation}</div>
                        </div>
                    </div>
                </div>
                <div class="back spread-left" style="background-image: url('{beat1_img}');">
                </div>
            </div>

            <!-- Leaf 2: Beat 1 Text / Beat 2 Image -->
            <div class="paper" id="p2">
                <div class="front spread-right" style="background-image: url('{beat1_img}');">
                    <div class="story-overlay {beat1_pos_class}">
                        <div class="text-content">
                            <div class="lang-en">{beat1_en}</div>
                            <div class="story-bilingual">
                                {beat1_paired}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="back spread-left" style="background-image: url('{beat2_img}');">
                </div>
            </div>

            <!-- Leaf 3: Beat 2 Text / Beat 3 Image -->
            <div class="paper" id="p3">
                <div class="front spread-right" style="background-image: url('{beat2_img}');">
                    <div class="story-overlay {beat2_pos_class}">
                        <div class="text-content">
                            <div class="lang-en">{beat2_en}</div>
                            <div class="story-bilingual">
                                {beat2_paired}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="back spread-left" style="background-image: url('{beat3_img}');">
                </div>
            </div>

            <!-- Leaf 4: Beat 3 Text / Beat 4 Image -->
            <div class="paper" id="p4">
                <div class="front spread-right" style="background-image: url('{beat3_img}');">
                    <div class="story-overlay {beat3_pos_class}">
                        <div class="text-content">
                            <div class="lang-en">{beat3_en}</div>
                            <div class="story-bilingual">
                                {beat3_paired}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="back spread-left" style="background-image: url('{beat4_img}');">
                </div>
            </div>

            <!-- Leaf 5: Beat 4 Text / Beat 5 Image -->
            <div class="paper" id="p5">
                <div class="front spread-right" style="background-image: url('{beat4_img}');">
                    <div class="story-overlay {beat4_pos_class}">
                        <div class="text-content">
                            <div class="lang-en">{beat4_en}</div>
                            <div class="story-bilingual">
                                {beat4_paired}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="back spread-left" style="background-image: url('{beat5_img}');">
                </div>
            </div>

            <!-- Leaf 6: Beat 5 Text / Beat 6 Image -->
            <div class="paper" id="p6">
                <div class="front spread-right" style="background-image: url('{beat5_img}');">
                    <div class="story-overlay {beat5_pos_class}">
                        <div class="text-content">
                            <div class="lang-en">{beat5_en}</div>
                            <div class="story-bilingual">
                                {beat5_paired}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="back spread-left" style="background-image: url('{beat6_img}');">
                </div>
            </div>

            <!-- Leaf 7: Beat 6 Text / Idiom Details -->
            <div class="paper" id="p7">
                <div class="front spread-right" style="background-image: url('{beat6_img}');">
                    <div class="story-overlay {beat6_pos_class}">
                        <div class="text-content">
                            <div class="lang-en">{beat6_en}</div>
                            <div class="story-bilingual">
                                {beat6_paired}
                            </div>
                        </div>
                    </div>
                </div>
                <div class="back">
                    <div class="text-content" style="justify-content: flex-start; padding: 24px;">
                        <h2>The Idiom / 成语解释</h2>
                        
                        <div class="idiom-details-grid">
                            <div class="idiom-detail-item">
                                <div class="idiom-detail-label">Characters</div>
                                <div class="idiom-detail-value char-value">{idiom_chars}</div>
                            </div>
                            <div class="idiom-detail-item">
                                <div class="idiom-detail-label">Pinyin</div>
                                <div class="idiom-detail-value" style="font-size: 1.1rem; font-weight: 600; padding-top: 4px;">{idiom_py}</div>
                            </div>
                            <div class="idiom-detail-item" style="grid-column: span 2;">
                                <div class="idiom-detail-label">Literal Meaning</div>
                                <div class="idiom-detail-value">{idiom_literal}</div>
                            </div>
                            <div class="idiom-detail-item" style="grid-column: span 2;">
                                <div class="idiom-detail-label">What it means</div>
                                <div class="idiom-detail-value" style="font-size: 0.92rem; line-height: 1.4;">{idiom_meaning}</div>
                            </div>
                        </div>

                        <div class="example-quote-container">
                            <span class="quote-mark">“</span>
                            <span class="example-quote-label">Use it in a sentence / 例句</span>
                            <p style="font-size: 0.95rem; margin: 0 0 8px 0; font-weight: 600; color: var(--text-primary); line-height: 1.4;">
                                {sentence_en}
                            </p>
                            <p class="lang-py" style="font-size: 0.85rem; margin: 0 0 4px 0; color: var(--text-secondary); font-style: italic;">
                                {sentence_py}
                            </p>
                            <p class="lang-cn" style="font-size: 1.15rem; margin: 0; font-weight: 700; color: var(--text-primary); line-height: 1.4;">
                                {sentence_cn_highlighted}
                            </p>
                        </div>
                    </div>
                </div>
            </div>

            <!-- Leaf 8: Story Spine / Back Cover -->
            <div class="paper" id="p8">
                <div class="front">
                    <div class="text-content" style="justify-content: flex-start; padding: 24px;">
                        <h2>The Story Spine / 故事大纲</h2>
                        <div class="timeline">
                            {timeline_html}
                        </div>
                    </div>
                </div>
                <div class="back">
                    <div class="back-cover-content">
                        {back_cover_inner_html}
                    </div>
                </div>
            </div>
        </div>
    </div>

    <!-- Bottom Page Controls -->
    <div class="bottom-controls">
        <button class="control-btn" id="prev-btn" onclick="goPrev()" title="Previous Page (Left Arrow)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="19" y1="12" x2="5" y2="12"></line>
                <polyline points="12 19 5 12 12 5"></polyline>
            </svg>
        </button>
        <button class="control-btn" id="next-btn" onclick="goNext()" title="Next Page (Right Arrow)">
            <svg width="20" height="20" viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.5" stroke-linecap="round" stroke-linejoin="round">
                <line x1="5" y1="12" x2="19" y2="12"></line>
                <polyline points="12 5 19 12 12 19"></polyline>
            </svg>
        </button>
    </div>

    <script>
        // Language Toggle Logic
        function setLanguageMode(mode) {{
            document.querySelectorAll('.toggle-btn').forEach(btn => {{
                btn.classList.toggle('active', btn.getAttribute('data-mode') === mode);
            }});
            
            const elementsEn = document.querySelectorAll('.lang-en');
            const elementsBilingual = document.querySelectorAll('.story-bilingual');
            const elementsPy = document.querySelectorAll('.lang-py');
            
            if (mode === 'english') {{
                elementsEn.forEach(el => el.style.display = 'block');
                elementsBilingual.forEach(el => el.style.display = 'none');
            }} else if (mode === 'chinese') {{
                elementsEn.forEach(el => el.style.display = 'none');
                elementsBilingual.forEach(el => el.style.display = 'block');
                elementsPy.forEach(el => el.style.display = 'none');
            }} else if (mode === 'chinese-pinyin') {{
                elementsEn.forEach(el => el.style.display = 'none');
                elementsBilingual.forEach(el => el.style.display = 'block');
                elementsPy.forEach(el => el.style.display = 'block');
            }}
            
            localStorage.setItem('chengyu-reader-lang', mode);
        }}

        // Book 3D Turn Logic
        const totalPapers = 8;
        let currentPaper = 1;
        const papers = [];
        
        for (let i = 1; i <= totalPapers; i++) {{
            papers.push(document.getElementById(`p${{i}}`));
        }}

        let transitionTimeout;

        function updateBook(transitioningPaper = null) {{
            const book = document.getElementById('book');
            
            // Adjust book container translation depending on whether it is open or closed
            if (currentPaper === 1) {{
                book.style.transform = 'translateX(25%)';
            }} else if (currentPaper === totalPapers + 1) {{
                book.style.transform = 'translateX(-25%)';
            }} else {{
                book.style.transform = 'translateX(0%)';
            }}

            // Add center binding spine shadow when open
            if (currentPaper > 1 && currentPaper <= totalPapers) {{
                book.classList.add('open');
            }} else {{
                book.classList.remove('open');
            }}

            // Set classes and dynamic static z-indices
            for (let i = 1; i <= totalPapers; i++) {{
                const paper = papers[i - 1];
                if (i < currentPaper) {{
                    paper.classList.add('flipped');
                    if (paper !== transitioningPaper) {{
                        paper.style.zIndex = i;
                    }}
                }} else {{
                    paper.classList.remove('flipped');
                    if (paper !== transitioningPaper) {{
                        paper.style.zIndex = totalPapers - i + 1;
                    }}
                }}
            }}

            // Handle temporary high z-index during transition to prevent page clipping
            if (transitioningPaper) {{
                transitioningPaper.style.zIndex = 100;
                if (transitionTimeout) clearTimeout(transitionTimeout);
                transitionTimeout = setTimeout(() => {{
                    for (let i = 1; i <= totalPapers; i++) {{
                        const paper = papers[i - 1];
                        if (i < currentPaper) {{
                            paper.style.zIndex = i;
                        }} else {{
                            paper.style.zIndex = totalPapers - i + 1;
                        }}
                    }}
                }}, 800);
            }}

            // Update nav controls disabled status
            document.getElementById('prev-btn').disabled = (currentPaper === 1);
            document.getElementById('next-btn').disabled = (currentPaper === totalPapers + 1);
        }}

        function goNext() {{
            if (currentPaper <= totalPapers) {{
                const paper = papers[currentPaper - 1];
                currentPaper++;
                updateBook(paper);
            }}
        }}

        function goPrev() {{
            if (currentPaper > 1) {{
                const paper = papers[currentPaper - 2];
                currentPaper--;
                updateBook(paper);
            }}
        }}

        // Setup page click triggers (click right page to go forward, left page to go back)
        papers.forEach((paper, idx) => {{
            paper.addEventListener('click', (e) => {{
                // Skip if clicking interactive elements like tables, links, buttons, scrollbars
                if (e.target.closest('button') || e.target.closest('a') || e.target.closest('table') || e.target.closest('.sentence-box')) {{
                    return;
                }}
                
                // Check if screen is mobile (scrolling layout) - disable 3D flip triggers
                if (window.innerWidth <= 768) {{
                    return;
                }}

                if (paper.classList.contains('flipped')) {{
                    goPrev();
                }} else {{
                    goNext();
                }}
            }});
        }});

        // Setup keyboard navigation
        document.addEventListener('keydown', (e) => {{
            if (window.innerWidth > 768) {{
                if (e.key === 'ArrowLeft') {{
                    goPrev();
                }} else if (e.key === 'ArrowRight') {{
                    goNext();
                }}
            }}
        }});

        // Initialize state on DOM load
        document.addEventListener('DOMContentLoaded', () => {{
            const savedMode = localStorage.getItem('chengyu-reader-lang') || 'chinese-pinyin';
            setLanguageMode(savedMode);
            updateBook();
        }});
    </script>
</body>
</html>
"""

def extract_section(title, text):
    pattern = r"## " + re.escape(title) + r".*?(?=\n##|\n---|\Z)"
    match = re.search(pattern, text, re.DOTALL)
    return match.group(0) if match else ""

def clean_markdown_formatting(text):
    text = re.sub(r"\*\*\*(.*?)\*\*\*", r"<strong><em>\1</em></strong>", text)
    text = re.sub(r"\*\*(.*?)\*\*", r"<strong>\1</strong>", text)
    text = re.sub(r"\*(.*?)\*", r"<em>\1</em>", text)
    return text.strip()

PINYIN_VOWELS = r"[aeoiuüāáǎàōóǒòēéěèīíǐìūúǔùǖǘǚǜü]"

def count_syllables(word):
    return len(re.findall(PINYIN_VOWELS + "+", word, re.IGNORECASE))

def is_pairable(char):
    if '\u4e00' <= char <= '\u9fff' or '\u3400' <= char <= '\u4dbf':
        return True
    if char.isalnum():
        return True
    return False

def is_trailing_punctuation(char):
    trailing_puncs = ",.!?;:)]}，。！？；：）】》”’"
    return char in trailing_puncs or char.isspace()

def align_words(cn_line, py_line):
    # Strip markdown asterisks and underscores used for formatting
    cn_line = cn_line.replace("*", "").replace("_", "")
    py_line = py_line.replace("*", "").replace("_", "")
    
    py_words = py_line.split()
    cn_chars = list(cn_line)
    cn_idx = 0
    cn_len = len(cn_chars)
    
    pairs = []
    
    for py_word in py_words:
        syllables = count_syllables(py_word)
        cn_segment = []
        
        # 1. Consume leading non-pairable characters
        while cn_idx < cn_len and not is_pairable(cn_chars[cn_idx]):
            cn_segment.append(cn_chars[cn_idx])
            cn_idx += 1
            
        # 2. Consume the required number of pairable characters
        pairables_consumed = 0
        while cn_idx < cn_len and pairables_consumed < syllables:
            if is_pairable(cn_chars[cn_idx]):
                pairables_consumed += 1
            cn_segment.append(cn_chars[cn_idx])
            cn_idx += 1
            
        # 3. Consume trailing non-pairable characters
        while cn_idx < cn_len and is_trailing_punctuation(cn_chars[cn_idx]):
            cn_segment.append(cn_chars[cn_idx])
            cn_idx += 1
            
        cn_word = "".join(cn_segment).strip()
        pairs.append((py_word, cn_word))
        
    if cn_idx < cn_len:
        remaining_cn = "".join(cn_chars[cn_idx:]).strip()
        if remaining_cn:
            if pairs:
                py_last, cn_last = pairs[-1]
                pairs[-1] = (py_last, (cn_last + " " + remaining_cn).strip())
            else:
                pairs.append(("", remaining_cn))
                
    return pairs

def clean_pinyin_line(line):
    line = line.strip()
    line = re.sub(r"^[\*_]+|[\*_]+$", "", line)
    return line.strip()

def pair_cn_py(cn_text, py_text):
    cn_paras = [p.strip() for p in cn_text.split("\n\n") if p.strip()]
    py_paras = [p.strip() for p in py_text.split("\n\n") if p.strip()]
    
    paired_paras = []
    max_paras = max(len(cn_paras), len(py_paras))
    
    for p_idx in range(max_paras):
        cn_para = cn_paras[p_idx] if p_idx < len(cn_paras) else ""
        py_para = py_paras[p_idx] if p_idx < len(py_paras) else ""
        
        cn_lines = [l.strip() for l in cn_para.splitlines() if l.strip()]
        py_lines = [l.strip() for l in py_para.splitlines() if l.strip()]
        
        paired_words_html = []
        max_lines = max(len(cn_lines), len(py_lines))
        
        for i in range(max_lines):
            cn_line = cn_lines[i] if i < len(cn_lines) else ""
            py_line = py_lines[i] if i < len(py_lines) else ""
            
            py_line_clean = clean_pinyin_line(py_line)
            
            # Align the words in the current line
            aligned_pairs = align_words(cn_line, py_line_clean)
            
            for py_w, cn_w in aligned_pairs:
                if py_w or cn_w:
                    paired_words_html.append(
                        f'<div class="sentence-pair">'
                        f'<div class="lang-py">{py_w}</div>'
                        f'<div class="lang-cn">{cn_w}</div>'
                        f'</div>'
                    )
        
        if paired_words_html:
            paired_paras.append(
                f'<div class="story-paragraph">\n'
                f'    ' + "\n    ".join(paired_words_html) + '\n'
                f'</div>'
            )
            
    return "\n".join(paired_paras)

def main():
    parser = argparse.ArgumentParser(description="Export a ChengYu Markdown book to an elegant HTML presentation.")
    parser.add_argument("file", help="Path to the book markdown file")
    parser.add_argument("-o", "--output", help="Path to output HTML file (defaults to book_name.html next to input)")
    args = parser.parse_args()

    if not os.path.exists(args.file):
        print(f"Error: File not found: {args.file}")
        sys.exit(1)

    content = None
    # Try strict decoding first
    for enc in ["utf-8-sig", "utf-16", "gb18030", "utf-8"]:
        try:
            with open(args.file, "r", encoding=enc) as f:
                content = f.read()
            break
        except (UnicodeError, LookupError):
            continue

    # If strict decoding fails, fall back to UTF-8 with character replacement
    if content is None:
        try:
            with open(args.file, "r", encoding="utf-8-sig", errors="replace") as f:
                content = f.read()
            print("Warning: Input file contained invalid bytes; decoded using UTF-8 with replacement characters.")
        except Exception as e:
            print(f"Error: Could not decode file {args.file}: {e}")
            sys.exit(1)

    # Parse headers
    lines = content.splitlines()
    title = clean_markdown_formatting(lines[0].replace("#", "").strip())
    subtitle_line = lines[1].replace("##", "").strip()
    subtitle = clean_markdown_formatting(subtitle_line)
    
    desc_match = re.search(r"\*(.*?)\*", content)
    description = desc_match.group(1).strip() if desc_match else ""

    # Split subtitle into pinyin and english for cover overlay
    cover_pinyin = ""
    cover_translation = ""
    if "—" in subtitle:
        parts = subtitle.split("—", 1)
        cover_pinyin = parts[0].strip()
        cover_translation = parts[1].strip()
    elif "-" in subtitle:
        parts = subtitle.split("-", 1)
        cover_pinyin = parts[0].strip()
        cover_translation = parts[1].strip()
    else:
        cover_pinyin = subtitle
        cover_translation = ""

    # Parse Title Page / Cover
    title_page_sec = extract_section("Title Page / 封面", content)
    cover_image_match = re.search(r"!\[.*?\]\((.*?)\)", title_page_sec)
    cover_image_path = cover_image_match.group(1) if cover_image_match else ""
    
    title_page_sec_clean = re.sub(r"🎨 \*\*Image prompt \(Gemini\):\*\*\s*\"(.*?)\"", "", title_page_sec, flags=re.DOTALL)
    title_page_clean = re.sub(r"<!--.*?-->", "", title_page_sec_clean, flags=re.DOTALL)
    
    curiosity_question = ""
    nudge = ""
    
    for line in title_page_clean.splitlines():
        line_str = line.strip()
        if not line_str or line_str.startswith("##") or line_str.startswith("🎨") or line_str.startswith("!["):
            continue
        if "Keep reading" in line_str or "继续" in line_str or "find out" in line_str:
            nudge = clean_markdown_formatting(line_str)
        else:
            if not curiosity_question:
                curiosity_question = clean_markdown_formatting(line_str)
                
    if not curiosity_question:
        curiosity_question = "What do you think will happen in this story? / 你觉得这个故事会发生什么呢？"
    if not nudge:
        nudge = "Keep reading to find out! / 继续往下读吧！"

    # Parse Beats
    beats = [
        ("Once there was… / 从前…", "Once there was"),
        ("Every day… / 每天…", "Every day"),
        ("Until one day… / 直到有一天…", "Until one day"),
        ("Because of that… / 因此…", "Because of that"),
        ("Until finally… / 最终…", "Until finally"),
        ("And ever since then… / 从那以后…", "And ever since then")
    ]

    beat_vars = {}
    for idx, (beat_name, label) in enumerate(beats, 1):
        beat_text = extract_section(beat_name, content)
        if not beat_text:
            continue
        
        img_match = re.search(r"!\[.*?\]\((.*?)\)", beat_text)
        img_path = img_match.group(1) if img_match else ""

        beat_text_clean = re.sub(r"🎨 \*\*Image prompt \(Gemini\):\*\*\s*\"(.*?)\"", "", beat_text, flags=re.DOTALL)
        
        beat_lines = []
        for line in beat_text_clean.splitlines():
            line_str = line.strip()
            if line_str.startswith("##") or line_str.startswith("🎨") or line_str.startswith("!["):
                continue
            beat_lines.append(line)
        
        clean_text = "\n".join(beat_lines).strip()
        
        cn_markers = ["从前", "每天", "直到有一天", "因此", "最终", "从那以后"]
        py_markers = ["Cóngqián", "Měi tiān", "Zhídào", "Yīncǐ", "Zuìzhōng", "Cóng"]
        
        cn_word = cn_markers[idx-1]
        py_word = py_markers[idx-1]
        
        cn_pos = -1
        cn_match = re.search(r"(?:^|\n)(?:\*\*|)\s*" + re.escape(cn_word), clean_text)
        if cn_match:
            cn_pos = cn_match.start()
            
        py_pos = -1
        py_match = re.search(r"(?:^|\n)\s*\*+\s*" + re.escape(py_word), clean_text)
        if py_match:
            py_pos = py_match.start()
        
        if py_pos == -1 or py_pos <= cn_pos:
            py_match = re.search(r"(?:^|\n)(?:\*|)\s*" + re.escape(py_word), clean_text, re.IGNORECASE)
            if py_match and py_match.start() > cn_pos:
                py_pos = py_match.start()

        en_text = ""
        cn_text = ""
        py_text = ""
        
        if cn_pos != -1 and py_pos != -1 and cn_pos < py_pos:
            en_text = clean_text[:cn_pos].strip()
            cn_text = clean_text[cn_pos:py_pos].strip()
            py_text = clean_text[py_pos:].strip()
        elif cn_pos != -1 and py_pos == -1:
            en_text = clean_text[:cn_pos].strip()
            cn_text = clean_text[cn_pos:].strip()
        else:
            en_text = clean_text

        # Pair Chinese and Pinyin line-by-line
        paired_html = pair_cn_py(cn_text, py_text)
        en_formatted = clean_markdown_formatting(en_text).replace("\n", "<br>")

        # Determine overlay positioning class (top vs bottom) based on layout balance
        # Beats 3, 4, 5 place the cow on the right/bottom-right, so text is positioned at the top.
        pos_class = "pos-top" if idx in [3, 4, 5] else "pos-bottom"

        beat_vars[f"beat{idx}_img"] = img_path
        beat_vars[f"beat{idx}_label"] = label
        beat_vars[f"beat{idx}_en"] = en_formatted
        beat_vars[f"beat{idx}_paired"] = paired_html
        beat_vars[f"beat{idx}_pos_class"] = pos_class

    # Parse Idiom
    idiom_sec = extract_section("The Idiom / 成语", content)
    idiom_chars = ""
    idiom_py = ""
    idiom_literal = ""
    idiom_meaning = ""
    
    chars_m = re.search(r"\*\*Characters\*\*\s*\|\s*(.*?)\s*\|", idiom_sec)
    py_m = re.search(r"\*\*Pinyin\*\*\s*\|\s*(.*?)\s*\|", idiom_sec)
    lit_m = re.search(r"\*\*Literal meaning\*\*\s*\|\s*(.*?)\s*\|", idiom_sec)
    mean_m = re.search(r"\*\*What it means\*\*\s*\|\s*(.*?)\s*\|", idiom_sec)

    idiom_chars = chars_m.group(1).strip() if chars_m else ""
    idiom_py = py_m.group(1).strip() if py_m else ""
    idiom_literal = lit_m.group(1).strip() if lit_m else ""
    idiom_meaning = mean_m.group(1).strip() if mean_m else ""

    # Parse sentence example
    sentence_lines = []
    sentence_part_match = re.search(r"\*\*Use it in a sentence:\*\*(.*?)(?=\n##|\n---|\Z)", idiom_sec, re.DOTALL)
    if sentence_part_match:
        for line in sentence_part_match.group(1).splitlines():
            line_str = line.strip()
            if line_str:
                sentence_lines.append(line_str)
    
    sentence_en = clean_markdown_formatting(sentence_lines[0]) if len(sentence_lines) > 0 else ""
    sentence_cn = clean_markdown_formatting(sentence_lines[1]) if len(sentence_lines) > 1 else ""
    sentence_py = clean_markdown_formatting(sentence_lines[2]) if len(sentence_lines) > 2 else ""

    # Highlight Chinese sentence idiom characters
    sentence_cn_highlighted = sentence_cn
    if idiom_chars:
        sentence_cn_highlighted = sentence_cn.replace(idiom_chars, f'<span style="color: var(--accent-red);">{idiom_chars}</span>')

    # Parse Story Spine timeline
    spine_sec = extract_section("The Story Spine, in 6 Beats", content)
    timeline_items = []
    badge_num = 1
    for line in spine_sec.splitlines():
        line_str = line.strip()
        if "|" in line_str and not line_str.startswith("| Beat") and not line_str.startswith("|---"):
            parts = [p.strip() for p in line_str.split("|")[1:-1]]
            if len(parts) >= 2:
                b_name_raw = parts[0].strip().strip("*").strip("_")
                b_name = clean_markdown_formatting(b_name_raw)
                b_desc = clean_markdown_formatting(parts[1])
                timeline_items.append(
                    f'                            <div class="timeline-item">\n'
                    f'                                <div class="timeline-badge">{badge_num}</div>\n'
                    f'                                <div class="timeline-content">\n'
                    f'                                    <strong>{b_name}</strong>\n'
                    f'                                    <p>{b_desc}</p>\n'
                    f'                                </div>\n'
                    f'                            </div>'
                )
                badge_num += 1
    
    timeline_html = "\n".join(timeline_items)

    # Determine back cover image path and inner HTML content
    base_name = os.path.splitext(os.path.basename(args.file))[0]
    prefix = base_name.split("_")[0]
    if args.output:
        html_dir = os.path.dirname(args.output)
    else:
        html_dir = os.path.dirname(args.file)
    
    rel_img_path = f"images/{base_name}/{prefix}_back_cover.png"
    abs_img_path = os.path.join(html_dir, rel_img_path)
    
    if os.path.exists(abs_img_path):
        back_cover_style = f"background-image: url('{rel_img_path}');\\n            background-size: cover;\\n            background-position: center;"
        back_cover_inner_html = "<!-- Clean full-bleed back cover image -->"
    else:
        back_cover_style = "background: #fdfbf7;"
        back_cover_inner_html = f"""
                        <h2 style="border-bottom: none; margin-bottom: 0;">THE END</h2>
                        <p style="color: var(--text-secondary); margin-bottom: 20px;">Thank you for reading!</p>
                        <div class="traditional-seal">{idiom_chars}</div>
        """

    # Format output HTML
    output_html = HTML_TEMPLATE.format(
        title=title,
        subtitle=subtitle,
        description=description,
        cover_image_path=cover_image_path,
        curiosity_question=curiosity_question,
        nudge=nudge,
        
        idiom_chars=idiom_chars,
        idiom_py=idiom_py,
        idiom_literal=idiom_literal,
        idiom_meaning=idiom_meaning,
        sentence_en=sentence_en,
        sentence_cn=sentence_cn,
        sentence_cn_highlighted=sentence_cn_highlighted,
        sentence_py=sentence_py,
        timeline_html=timeline_html,
        back_cover_style=back_cover_style,
        back_cover_inner_html=back_cover_inner_html,
        cover_pinyin=cover_pinyin,
        cover_translation=cover_translation,
        
        **beat_vars
    )

    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    if args.output:
        output_path = args.output
    else:
        output_path = os.path.splitext(args.file)[0] + ".html"

    with open(output_path, "w", encoding="utf-8") as f:
        f.write(output_html)

    print(f"Successfully exported to HTML: {output_path}")

if __name__ == "__main__":
    main()
