import os
import re
import sys
import argparse

class BookValidator:
    def __init__(self, file_path):
        self.file_path = file_path
        self.filename = os.path.basename(file_path)
        self.errors = []
        self.warnings = []

    def log_error(self, message):
        self.errors.append(message)

    def log_warning(self, message):
        self.warnings.append(message)

    def validate(self):
        if not os.path.exists(self.file_path):
            self.log_error(f"File does not exist: {self.file_path}")
            return False

        # 1. Filename validation
        # e.g., 01_dui_niu_tan_qin.md
        filename_pattern = r"^\d{2}_[a-z0-9_]+\.md$"
        if not re.match(filename_pattern, self.filename):
            self.log_error(f"Filename '{self.filename}' does not match pattern: NN_pinyin_no_tones.md")

        content = None
        for enc in ["utf-8-sig", "utf-16", "gb18030", "utf-8"]:
            try:
                with open(self.file_path, "r", encoding=enc) as f:
                    content = f.read()
                break
            except (UnicodeError, LookupError):
                continue

        if content is None:
            try:
                with open(self.file_path, "r", encoding="utf-8-sig", errors="replace") as f:
                    content = f.read()
            except Exception as e:
                self.log_error(f"Could not read file: {e}")
                return False

        lines = content.splitlines()
        
        # 2. Basic layout checks
        if not lines:
            self.log_error("File is empty")
            return False

        # Header checking
        if not lines[0].startswith("# "):
            self.log_error("Line 1 must be a Level 1 header with the idiom characters, e.g., '# 对牛弹琴'")
        
        if len(lines) > 1 and not lines[1].startswith("## "):
            self.log_error("Line 2 must be a Level 2 header with pinyin and translation, e.g., '## Duì Niú Tán Qín — Playing Music to a Cow'")

        # Section presence checks
        sections = [
            r"## Visual Reference",
            r"## Title Page / 封面",
            r"## Once there was… / 从前…",
            r"## Every day… / 每天…",
            r"## Until one day… / 直到有一天…",
            r"## Because of that… / 因此…",
            r"## Until finally… / 最终…",
            r"## And ever since then… / 从那以后…",
            r"## The Idiom / 成语",
            r"## The Story Spine, in 6 Beats"
        ]

        for section in sections:
            if not re.search(r"^" + re.escape(section), content, re.MULTILINE):
                self.log_error(f"Missing required section header: '{section}'")

        # 3. Parse Visual Reference
        style_match = re.search(r"\*\*Style:\*\* (.*?)$", content, re.MULTILINE)
        if not style_match:
            self.log_error("Missing '**Style:**' in Visual Reference section")
            style_desc = None
        else:
            style_desc = style_match.group(1).strip()

        # Parse character descriptions
        # Format e.g.: **Gong Mingyi (the musician):** description
        character_descriptions = {}
        # Find all lines in the Visual Reference section that define a character
        # Visual reference block is between '## Visual Reference' and the next '---' or '##'
        vis_ref_sec = re.search(r"## Visual Reference.*?(?=\n##|\n---|\Z)", content, re.DOTALL)
        if vis_ref_sec:
            char_lines = re.findall(r"\*\*(.*?)\*\* (.*?)$", vis_ref_sec.group(0), re.MULTILINE)
            for char_name, char_desc in char_lines:
                if char_name == "Style":
                    continue
                # We strip potential colons and whitespaces
                char_name_clean = char_name.rstrip(":").strip()
                character_descriptions[char_name_clean] = char_desc.strip().rstrip(".")
        else:
            self.log_error("Could not parse Visual Reference block")

        # 4. Check Title Page / 封面
        title_page_sec = re.search(r"## Title Page / 封面.*?(?=\n##|\n---|\Z)", content, re.DOTALL)
        if title_page_sec:
            tp_text = title_page_sec.group(0)
            # Should have image prompt
            if "🎨 **Image prompt (Gemini):**" not in tp_text:
                self.log_error("Title Page missing '🎨 **Image prompt (Gemini):**'")
            
            # Check for image link
            if not re.search(r"!\[.*?\]\((.*?)\)", tp_text):
                self.log_error("Title Page missing cover image link")
            
            # Check for all three options (either commented or uncommented)
            if "Option 1" not in tp_text or "Prediction" not in tp_text:
                self.log_error("Title Page missing Curiosity Gap Option 1: Prediction")
            if "Option 2" not in tp_text or "Mystery" not in tp_text:
                self.log_error("Title Page missing Curiosity Gap Option 2: Mystery")
            if "Option 3" not in tp_text or "Wisdom Discovery" not in tp_text:
                self.log_error("Title Page missing Curiosity Gap Option 3: Wisdom Discovery")
            
            # Now let's count how many options are uncommented.
            # We strip the image prompt block, then comments, and see what lines remain.
            tp_clean_for_val = re.sub(r"🎨 \*\*Image prompt \(Gemini\):\*\*\s*\"(.*?)\"", "", tp_text, flags=re.DOTALL)
            tp_no_comments = re.sub(r"<!--.*?-->", "", tp_clean_for_val, flags=re.DOTALL)
            
            active_options = []
            nudge_found = False
            for line in tp_no_comments.splitlines():
                line_str = line.strip()
                if not line_str or line_str.startswith("##") or line_str.startswith("🎨") or line_str.startswith("![") or line_str.startswith("---"):
                    continue
                if "Keep reading to find out" in line_str or "继续" in line_str or "find out" in line_str:
                    nudge_found = True
                else:
                    active_options.append(line_str)
            
            if len(active_options) != 1:
                self.log_error(f"Title Page must have exactly one active (uncommented) curiosity gap option. Found: {active_options}")
            if not nudge_found:
                self.log_error("Title Page missing closing nudge: 'Keep reading to find out! / 继续往下读吧！'")
        
        # 5. Check the 6 beats content structure
        beats = [
            ("Once there was… / 从前…", "Once there was", "从前，", "*Cóngqián,"),
            ("Every day… / 每天…", "Every day", "每天，", "*Měi tiān,"),
            ("Until one day… / 直到有一天…", "Until one day", "直到有一天，", "*Zhídào yǒu yī tiān,"),
            ("Because of that… / 因此…", "Because of that", "因此，", "*Yīncǐ,"),
            ("Until finally… / 最终…", "Until finally", "最终，", "*Zuìzhōng,"),
            ("And ever since then… / 从那以后…", "And ever since then", "从那以后，", "*Cóng nà")
        ]

        for i, (beat_name, en_start, cn_start, py_start) in enumerate(beats, 1):
            beat_sec_match = re.search(r"## " + re.escape(beat_name) + r".*?(?=\n##|\n---|\Z)", content, re.DOTALL)
            if not beat_sec_match:
                # Already logged as missing section header, skip detailed checks
                continue
            
            beat_text = beat_sec_match.group(0)
            
            # Check for English, Chinese, Pinyin lines
            # English should contain en_start (allow either bolded or plain, but guide says bolded)
            if en_start not in beat_text:
                self.log_error(f"Beat {i} ({beat_name}) English line must start with '{en_start}'")
            if cn_start not in beat_text:
                # Let's search with flexible whitespace/comma
                cn_clean = cn_start.replace("，", "").replace("、", "").replace(" ", "")
                if cn_clean not in beat_text.replace("，", "").replace("、", "").replace(" ", ""):
                    self.log_error(f"Beat {i} ({beat_name}) Chinese line must start with '{cn_start}'")
            if py_start not in beat_text:
                py_clean = py_start.replace(" ", "").strip("*").strip(",")
                if py_clean not in beat_text.replace(" ", "").replace("*", "").replace(",", ""):
                    self.log_error(f"Beat {i} ({beat_name}) Pinyin line should start with '{py_start}' and be in italics")

            # Check image prompt block
            img_prompt_match = re.search(r"🎨 \*\*Image prompt \(Gemini\):\*\*\s*\"(.*?)\"", beat_text, re.DOTALL)
            if not img_prompt_match:
                self.log_error(f"Beat {i} ({beat_name}) missing '🎨 **Image prompt (Gemini):**' followed by quoted prompt")
            else:
                prompt_content = img_prompt_match.group(1)
                
                # Check style inclusion
                if i < 6 and style_desc and style_desc not in prompt_content:
                    self.log_error(f"Beat {i} ({beat_name}) image prompt does not contain the locked style description verbatim")

                # Check character descriptions
                # If a character's name (or key part of name) is mentioned, their locked description must be present
                if i < 6:
                    for char_name, char_desc in character_descriptions.items():
                        # Check if the name appears in the prompt outside of the exact description
                        # Simple heuristic: if character name is in the prompt, let's verify description is there
                        # To avoid false positive, we clean the name (e.g. "Gong Mingyi" or "First Painter")
                        short_name = char_name.split("(")[0].strip()
                        if short_name in prompt_content:
                            if char_desc not in prompt_content:
                                self.log_error(f"Beat {i} ({beat_name}) image prompt mentions '{short_name}' but does not include the locked description verbatim: '{char_desc}'")

        # 6. Check The Idiom table
        idiom_sec = re.search(r"## The Idiom / 成语.*?(?=\n##|\n---|\Z)", content, re.DOTALL)
        if idiom_sec:
            idiom_text = idiom_sec.group(0)
            if "| **Characters** |" not in idiom_text or "| **Pinyin** |" not in idiom_text or "| **Literal meaning** |" not in idiom_text or "| **What it means** |" not in idiom_text:
                self.log_error("The Idiom section table structure is missing required rows (Characters, Pinyin, Literal meaning, What it means)")
            if "**Use it in a sentence:**" not in idiom_text:
                self.log_error("The Idiom section missing '**Use it in a sentence:**'")
        
        # 7. Check The Story Spine table
        spine_sec = re.search(r"## The Story Spine, in 6 Beats.*?(?=\n##|\n---|\Z)", content, re.DOTALL)
        if spine_sec:
            spine_text = spine_sec.group(0)
            required_beats = [
                "**Once there was…**",
                "**Every day…**",
                "**Until one day…**",
                "**Because of that…**",
                "**Until finally…**",
                "**And ever since then…**"
            ]
            for rb in required_beats:
                if rb not in spine_text:
                    self.log_error(f"The Story Spine table missing beat: '{rb}'")

        return len(self.errors) == 0

def main():
    # Force UTF-8 encoding on stdout and stderr to prevent UnicodeEncodeErrors on Windows terminals
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
    if hasattr(sys.stderr, "reconfigure"):
        sys.stderr.reconfigure(encoding="utf-8")

    parser = argparse.ArgumentParser(description="Validate ChengYu book markdown files.")
    parser.add_argument("file", help="Path to the markdown file to validate")
    args = parser.parse_args()

    validator = BookValidator(args.file)
    success = validator.validate()

    if success:
        print(f"✅ {validator.filename} is VALID!")
        if validator.warnings:
            print(f"\nWarnings ({len(validator.warnings)}):")
            for warning in validator.warnings:
                print(f"  - {warning}")
        sys.exit(0)
    else:
        print(f"❌ {validator.filename} is INVALID!")
        print(f"\nErrors ({len(validator.errors)}):")
        for error in validator.errors:
            print(f"  - {error}")
        if validator.warnings:
            print(f"\nWarnings ({len(validator.warnings)}):")
            for warning in validator.warnings:
                print(f"  - {warning}")
        sys.exit(1)

if __name__ == "__main__":
    main()
