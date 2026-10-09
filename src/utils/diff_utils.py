import difflib

def generate_html_diff(old_text: str, new_text: str) -> str:
    """
    Generate an HTML diff between old_text and new_text highlighting additions and deletions.
    """
    old_words = old_text.split()
    new_words = new_text.split()
    
    differ = difflib.SequenceMatcher(None, old_words, new_words)
    result = []
    
    for tag, i1, i2, j1, j2 in differ.get_opcodes():
        if tag == 'equal':
            result.append(" ".join(old_words[i1:i2]))
        elif tag == 'delete':
            deleted = " ".join(old_words[i1:i2])
            result.append(f"<span style='color:red; text-decoration:line-through;'>{deleted}</span>")
        elif tag == 'insert':
            inserted = " ".join(new_words[j1:j2])
            result.append(f"<span style='color:green; font-weight:bold;'>{inserted}</span>")
        elif tag == 'replace':
            deleted = " ".join(old_words[i1:i2])
            inserted = " ".join(new_words[j1:j2])
            result.append(f"<span style='color:red; text-decoration:line-through;'>{deleted}</span>")
            result.append(f"<span style='color:green; font-weight:bold;'>{inserted}</span>")
            
    return " ".join(result).replace("\n", "<br>")
