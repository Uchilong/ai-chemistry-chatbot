"""Chemistry Specialized Keyboard Component for Streamlit."""

import streamlit as st
from typing import Optional, Callable


class ChemistryKeyboard:
    """Interactive chemistry keyboard for Streamlit - helps input chemical formulas and symbols."""
    
    def __init__(self):
        """Initialize the chemistry keyboard."""
        self.symbol_categories = {
            "Elements": {
                "H": "Hydrogen", "C": "Carbon", "N": "Nitrogen", "O": "Oxygen",
                "S": "Sulfur", "P": "Phosphorus", "F": "Fluorine", "Cl": "Chlorine",
                "Br": "Bromine", "I": "Iodine", "Na": "Sodium", "K": "Potassium",
                "Ca": "Calcium", "Fe": "Iron", "Cu": "Copper", "Zn": "Zinc",
                "Ag": "Silver", "Au": "Gold", "Pb": "Lead", "Hg": "Mercury",
                "Mg": "Magnesium", "Al": "Aluminum", "Si": "Silicon", "Cr": "Chromium"
            },
            "Bonds & Reactions": {
                "→": "Forward arrow", "⇌": "Equilibrium", "←": "Backward arrow",
                "=": "Double bond", "≡": "Triple bond", "•": "Electron",
                "Δ": "Heat", "hν": "Photon/Light", "[•]": "Radical",
                "↑": "Gas", "↓": "Precipitate", "|": "Aqueous"
            },
            "Numbers & Operators": {
                "₀": "Subscript 0", "₁": "Subscript 1", "₂": "Subscript 2",
                "₃": "Subscript 3", "₄": "Subscript 4", "₅": "Subscript 5",
                "⁺": "Superscript +", "⁻": "Superscript -", "⁰": "Superscript 0",
                "²⁺": "2+ charge", "³⁻": "3- charge"
            },
            "Common Ions": {
                "H⁺": "H⁺", "OH⁻": "OH⁻", "Na⁺": "Na⁺", "Cl⁻": "Cl⁻",
                "SO₄²⁻": "SO₄²⁻", "NO₃⁻": "NO₃⁻", "HCO₃⁻": "HCO₃⁻",
                "NH₄⁺": "NH₄⁺", "Ca²⁺": "Ca²⁺", "CO₃²⁻": "CO₃²⁻"
            },
            "Parentheses": {
                "(": "Open", ")": "Close", "[": "Bracket [",
                "]": "Bracket ]", "{": "Brace {", "}": "Brace }"
            }
        }
    
    def render(self, on_symbol_click: Optional[Callable[[str], None]] = None) -> Optional[str]:
        """
        Render the chemistry keyboard in Streamlit.
        
        Args:
            on_symbol_click: Callback function when a symbol is clicked
        
        Returns:
            The selected symbol if clicked
        """
        selected_symbol = None
        
        st.subheader("⚗️ Chemistry Keyboard")
        
        # Create tabs for different categories
        tabs = st.tabs(list(self.symbol_categories.keys()))
        
        for tab, category in zip(tabs, self.symbol_categories.keys()):
            with tab:
                symbols = self.symbol_categories[category]
                
                # Create grid layout (5 buttons per row)
                cols_per_row = 5
                symbol_list = list(symbols.items())
                
                for i in range(0, len(symbol_list), cols_per_row):
                    cols = st.columns(cols_per_row)
                    
                    for col_idx, col in enumerate(cols):
                        item_idx = i + col_idx
                        if item_idx < len(symbol_list):
                            symbol, description = symbol_list[item_idx]
                            with col:
                                # Create button with tooltip
                                if st.button(
                                    symbol,
                                    key=f"symbol_{category}_{item_idx}",
                                    use_container_width=True,
                                    help=description
                                ):
                                    selected_symbol = symbol
                                    if on_symbol_click:
                                        on_symbol_click(symbol)
        
        return selected_symbol
    
    def render_quick_access(self) -> Optional[str]:
        """Render a quick access toolbar for most common chemistry symbols."""
        st.markdown("### ⚡ Quick Access")
        
        quick_symbols = {
            "→": "Reaction", "⇌": "Equilibrium", "H₂O": "Water",
            "H⁺": "H⁺", "OH⁻": "OH⁻", "NaCl": "NaCl",
            "CO₂": "CO₂", "NH₃": "NH₃", "CH₄": "CH₄",
            "°C": "Celsius", "Δ": "Heat", "hν": "Light"
        }
        
        cols = st.columns(len(quick_symbols))
        selected = None
        
        for col_idx, (symbol, label) in enumerate(quick_symbols.items()):
            with cols[col_idx]:
                if st.button(symbol, key=f"quick_{symbol}", use_container_width=True, help=label):
                    selected = symbol
        
        return selected
    
    @staticmethod
    def insert_into_text(current_text: str, symbol: str, cursor_pos: Optional[int] = None) -> str:
        """
        Insert a symbol into text at cursor position.
        
        Args:
            current_text: Current text
            symbol: Symbol to insert
            cursor_pos: Position to insert (default: end)
        
        Returns:
            Updated text
        """
        if cursor_pos is None:
            cursor_pos = len(current_text)
        
        new_text = current_text[:cursor_pos] + symbol + current_text[cursor_pos:]
        return new_text


def chemistry_keyboard_demo():
    """Demo function to show chemistry keyboard in action."""
    st.write("### Chemistry Keyboard Demo")
    
    # Initialize keyboard
    keyboard = ChemistryKeyboard()
    
    # Session state for text input
    if "chem_input" not in st.session_state:
        st.session_state.chem_input = ""
    
    # Quick access toolbar
    st.write("**Quick Access Symbols:**")
    quick_symbol = keyboard.render_quick_access()
    
    if quick_symbol:
        st.session_state.chem_input = ChemistryKeyboard.insert_into_text(
            st.session_state.chem_input,
            quick_symbol
        )
    
    # Main keyboard
    st.write("**Full Chemistry Keyboard:**")
    selected_symbol = keyboard.render()
    
    if selected_symbol:
        st.session_state.chem_input = ChemistryKeyboard.insert_into_text(
            st.session_state.chem_input,
            selected_symbol
        )
    
    # Display current input
    st.write("**Your Input:**")
    col1, col2 = st.columns([0.8, 0.2])
    with col1:
        new_input = st.text_input(
            "Chemical formula/equation:",
            value=st.session_state.chem_input,
            key="chem_text_input"
        )
        if new_input != st.session_state.chem_input:
            st.session_state.chem_input = new_input
    
    with col2:
        if st.button("Clear", use_container_width=True):
            st.session_state.chem_input = ""
            st.rerun()
    
    # Display formatted version
    if st.session_state.chem_input:
        st.info(f"**Formula:** {st.session_state.chem_input}")


if __name__ == "__main__":
    chemistry_keyboard_demo()
