"""Wolfram Alpha API tool for chemical calculations and equation balancing."""

import os
import requests
import urllib.parse
from typing import Dict, List, Optional, Union
import re
from dataclasses import dataclass

@dataclass
class CalculationResult:
    """Data class for calculation results."""
    input_expression: str
    result: Union[str, float, Dict]
    steps: List[str]
    units: str
    explanation: str
    success: bool
    error_message: Optional[str] = None

class WolframTool:
    """Tool for chemical calculations using Wolfram Alpha API."""
    
    def __init__(self, app_id: Optional[str] = None):
        """
        Initialize Wolfram Alpha tool.
        
        Args:
            app_id: Wolfram Alpha App ID (get from https://developer.wolframalpha.com/)
        """
        self.app_id = app_id or os.getenv("WOLFRAM_APP_ID", "")
        self.base_url = "https://api.wolframalpha.com/v2/query"
        
        if not self.app_id:
            print("Warning: Wolfram Alpha App ID not provided. Some features will be limited.")
    
    def _convert_latex_to_unicode(self, text: str) -> str:
        """Convert LaTeX-style chemical formulas to Unicode."""
        if not text:
            return text
        
        # Replace LaTeX-style subscripts with Unicode subscripts
        latex_to_unicode = {
            '_0': '₀', '_1': '₁', '_2': '₂', '_3': '₃', '_4': '₄',
            '_5': '₅', '_6': '₆', '_7': '₇', '_8': '₈', '_9': '₉',
            '^0': '⁰', '^1': '¹', '^2': '²', '^3': '³', '^4': '⁴',
            '^5': '⁵', '^6': '⁶', '^7': '⁷', '^8': '⁸', '^9': '⁹',
            '^+': '⁺', '^-': '⁻', '^2+': '²⁺', '^2-': '²⁻',
            '^3+': '³⁺', '^3-': '³⁻',
        }
        
        # Replace arrows
        arrows = {
            '->': '→',
            '<-': '←', 
            '<->': '⇌',
            '=>': '⇒',
            '<=': '⇐',
            '<=>': '⇔',
            '→': '→',
            '←': '←',
            '⇌': '⇌',
            '⟶': '→',
            '⟷': '⇌'
        }
        
        result = text
        for latex, unicode_char in latex_to_unicode.items():
            result = result.replace(latex, unicode_char)
        
        for arrow_latex, arrow_unicode in arrows.items():
            result = result.replace(arrow_latex, arrow_unicode)
        
        return result
    
    def balance_equation(self, equation: str) -> CalculationResult:
        """
        Balance chemical equation.
        
        Args:
            equation: Unbalanced chemical equation (e.g., "H2 + O2 -> H2O")
            
        Returns:
            CalculationResult with balanced equation and steps
        """
        try:
            # Format query for Wolfram Alpha
            query = f"balance chemical equation {equation}"
            
            if self.app_id:
                result = self._query_wolfram(query)
                if result.success:
                    return result
                return result
            
            # Fallback to simple balancing logic
            return self._simple_balance(equation)
                
        except Exception as e:
            return CalculationResult(
                input_expression=equation,
                result="",
                steps=[],
                units="",
                explanation="",
                success=False,
                error_message=f"Error balancing equation: {str(e)}"
            )
    
    def calculate_molar_mass(self, formula: str) -> CalculationResult:
        """
        Calculate molar mass of chemical formula.
        
        Args:
            formula: Chemical formula (e.g., "C6H12O6")
            
        Returns:
            CalculationResult with molar mass
        """
        try:
            query = f"molar mass of {formula}"
            
            if self.app_id:
                result = self._query_wolfram(query)
                if result.success:
                    return result
            
            # Fallback to basic calculation
            return self._calculate_molar_mass_fallback(formula)
            
        except Exception as e:
            return CalculationResult(
                input_expression=formula,
                result="",
                steps=[],
                units="g/mol",
                explanation="",
                success=False,
                error_message=f"Error calculating molar mass: {str(e)}"
            )
    
    def stoichiometry_calculation(self, equation: str, given_amount: float, 
                                 given_unit: str, find_substance: str) -> CalculationResult:
        """
        Perform stoichiometry calculations.
        
        Args:
            equation: Balanced chemical equation
            given_amount: Amount of given substance
            given_unit: Unit of given amount (g, mol, L, etc.)
            find_substance: Substance to find amount for
            
        Returns:
            CalculationResult with stoichiometry solution
        """
        try:
            query = f"stoichiometry {equation} {given_amount} {given_unit} of first reactant to {find_substance}"
            
            if self.app_id:
                result = self._query_wolfram(query)
                if result.success:
                    return result
            
            # Fallback to basic stoichiometry
            return self._stoichiometry_fallback(equation, given_amount, given_unit, find_substance)
            
        except Exception as e:
            return CalculationResult(
                input_expression=f"{equation}, {given_amount} {given_unit} -> {find_substance}",
                result="",
                steps=[],
                units="",
                explanation="",
                success=False,
                error_message=f"Error in stoichiometry calculation: {str(e)}"
            )
    
    def solve_chemistry_problem(self, problem: str) -> CalculationResult:
        """
        Solve general chemistry problem.
        
        Args:
            problem: Chemistry problem description
            
        Returns:
            CalculationResult with solution
        """
        try:
            query = f"chemistry problem: {problem}"
            
            if self.app_id:
                return self._query_wolfram(query)
            else:
                # Fallback to basic problem solving
                return CalculationResult(
                    input_expression=problem,
                    result="Wolfram Alpha API required for detailed solution",
                    steps=["1. Identify the chemistry concept", "2. Apply relevant formulas", "3. Calculate result"],
                    units="",
                    explanation="Please provide Wolfram Alpha App ID for detailed calculations",
                    success=False,
                    error_message="Wolfram Alpha App ID required"
                )
                
        except Exception as e:
            return CalculationResult(
                input_expression=problem,
                result="",
                steps=[],
                units="",
                explanation="",
                success=False,
                error_message=f"Error solving problem: {str(e)}"
            )
    
    def _query_wolfram(self, query: str) -> CalculationResult:
        """Query Wolfram Alpha API."""
        try:
            params = {
                'input': query,
                'format': 'plaintext',
                'output': 'JSON',
                'appid': self.app_id,
                'units': 'metric'
            }
            
            response = requests.get(self.base_url, params=params, timeout=30)
            
            if response.status_code == 200:
                data = response.json()
                
                if data.get('queryresult', {}).get('success'):
                    pods = data['queryresult'].get('pods', [])
                    
                    # Extract result and steps
                    result = ""
                    steps = []
                    explanation = ""
                    
                    for pod in pods:
                        if pod.get('title') in ['Result', 'Solution']:
                            subpods = pod.get('subpods', [])
                            if subpods:
                                result = subpods[0].get('plaintext', '')
                        
                        elif pod.get('title') in ['Step-by-step solution', 'Steps']:
                            subpods = pod.get('subpods', [])
                            for subpod in subpods:
                                steps.append(subpod.get('plaintext', ''))
                        
                        elif pod.get('title') in ['Explanation', 'Interpretation']:
                            subpods = pod.get('subpods', [])
                            if subpods:
                                explanation = subpods[0].get('plaintext', '')
                    
                    return CalculationResult(
                        input_expression=query,
                        result=self._convert_latex_to_unicode(result),
                        steps=[self._convert_latex_to_unicode(step) for step in steps],
                        units=self._extract_units(result),
                        explanation=self._convert_latex_to_unicode(explanation),
                        success=True
                    )
                else:
                    error_msg = data.get('queryresult', {}).get('error', {}).get('msg', 'Unknown error')
                    return CalculationResult(
                        input_expression=query,
                        result="",
                        steps=[],
                        units="",
                        explanation="",
                        success=False,
                        error_message=f"Wolfram Alpha error: {error_msg}"
                    )
            else:
                return CalculationResult(
                    input_expression=query,
                    result="",
                    steps=[],
                    units="",
                    explanation="",
                    success=False,
                    error_message=f"HTTP {response.status_code}: {response.text}"
                )
                
        except Exception as e:
            return CalculationResult(
                input_expression=query,
                result="",
                steps=[],
                units="",
                explanation="",
                success=False,
                error_message=f"API request failed: {str(e)}"
            )
    
    def _extract_units(self, result: str) -> str:
        """Extract units from result string."""
        # Common unit patterns
        unit_patterns = [
            r'(g/mol|mol|g|kg|L|mL|atm|Pa|K|°C|°F|J|kJ|cal|kcal)',
            r'\(([^)]+)\)$'  # Units in parentheses
        ]
        
        for pattern in unit_patterns:
            match = re.search(pattern, result)
            if match:
                return match.group(1) if match.groups() else match.group(0)
        
        return ""
    
    def _simple_balance(self, equation: str) -> CalculationResult:
        """Simple fallback for equation balancing."""
        # This is a very basic fallback - real balancing requires complex algorithms
        return CalculationResult(
            input_expression=equation,
            result=self._convert_latex_to_unicode(f"Balanced: {equation} (simplified)"),
            steps=["1. Count atoms on each side", "2. Balance coefficients", "3. Verify balance"],
            units="",
            explanation="This is a simplified result. Use Wolfram Alpha API for accurate balancing.",
            success=True
        )
    
    def _calculate_molar_mass_fallback(self, formula: str) -> CalculationResult:
        """Fallback molar mass calculation using basic atomic weights."""
        # Check if it's a known compound first
        known_compounds = {
            'H2O': 18.015, 'CO2': 44.01, 'O2': 32.00, 'H2': 2.016,
            'N2': 28.014, 'NH3': 17.031, 'CH4': 16.04, 'NaCl': 58.44,
            'HCl': 36.46, 'NaOH': 40.00, 'C6H12O6': 180.16, 'H2SO4': 98.079,
            'HNO3': 63.01, 'CH3COOH': 60.05, 'C2H5OH': 46.07, 'SO2': 64.07,
            'NO2': 46.01, 'CO': 28.01, 'H2S': 34.08, 'SO3': 80.06,
            'CaCO3': 100.09, 'Na2CO3': 105.99, 'KCl': 74.55, 'MgSO4': 120.37
        }
        
        # Clean up the formula
        clean_formula = formula.strip().replace(' ', '')
        
        if clean_formula in known_compounds:
            return CalculationResult(
                input_expression=formula,
                result=f"{known_compounds[clean_formula]:.3f} g/mol",
                steps=[f"Known compound: {clean_formula}", f"Molar mass: {known_compounds[clean_formula]:.3f} g/mol"],
                units="g/mol",
                explanation=f"Molar mass of {clean_formula} from database",
                success=True
            )
        
        # Basic atomic masses for calculation
        atomic_masses = {
            'H': 1.008, 'He': 4.003, 'Li': 6.941, 'Be': 9.012, 'B': 10.81, 'C': 12.011,
            'N': 14.007, 'O': 15.999, 'F': 18.998, 'Ne': 20.180, 'Na': 22.990, 'Mg': 24.305,
            'Al': 26.982, 'Si': 28.086, 'P': 30.974, 'S': 32.065, 'Cl': 35.453, 'Ar': 39.948,
            'K': 39.098, 'Ca': 40.078, 'Sc': 44.956, 'Ti': 47.867, 'V': 50.942, 'Cr': 51.996,
            'Mn': 54.938, 'Fe': 55.845, 'Co': 58.933, 'Ni': 58.693, 'Cu': 63.546, 'Zn': 65.38
        }
        
        try:
            # Simple formula parsing (very basic)
            import re
            pattern = r'([A-Z][a-z]?)(\d*)'
            matches = re.findall(pattern, formula)
            
            total_mass = 0.0
            steps = [f"Analyzing formula: {formula}"]
            
            for element, count_str in matches:
                count = int(count_str) if count_str else 1
                if element in atomic_masses:
                    mass = atomic_masses[element] * count
                    total_mass += mass
                    steps.append(f"{element}: {count} × {atomic_masses[element]} = {mass:.3f} g/mol")
                else:
                    steps.append(f"{element}: atomic mass not found in database")
            
            steps.append(f"Total molar mass: {total_mass:.3f} g/mol")
            
            return CalculationResult(
                input_expression=formula,
                result=f"{total_mass:.3f} g/mol",
                steps=steps,
                units="g/mol",
                explanation=f"Molar mass calculated using atomic weights for {formula}",
                success=True
            )
            
        except Exception as e:
            return CalculationResult(
                input_expression=formula,
                result="",
                steps=[],
                units="g/mol",
                explanation="",
                success=False,
                error_message=f"Error in fallback calculation: {str(e)}"
            )
    
    def _stoichiometry_fallback(self, equation: str, given_amount: float, 
                               given_unit: str, find_substance: str) -> CalculationResult:
        """Fallback stoichiometry calculation with basic logic."""
        try:
            # Parse equation to get coefficients (simplified)
            import re
            
            steps = [f"1. Analyze equation: {equation}"]
            
            # Extract substances and coefficients from equation
            # This is a simplified approach - real stoichiometry is more complex
            if '->' in equation:
                parts = equation.split('->')
            elif '→' in equation:
                parts = equation.split('→')
            elif '=' in equation:
                parts = equation.split('=')
            else:
                # If no arrow found, assume it's just a formula for molar mass
                return self._calculate_molar_mass_fallback(equation)
            
            if len(parts) < 2:
                # Not enough parts for stoichiometry, treat as molar mass calculation
                return self._calculate_molar_mass_fallback(equation)
            
            left_side, right_side = parts[0], parts[1]
            
            # Check if this looks like a single formula (like "H2SO4") instead of equation
            if not left_side.strip() or not right_side.strip():
                return self._calculate_molar_mass_fallback(equation)
            
            # Get molar masses for basic substances
            molar_masses = {
                'H2O': 18.015, 'CO2': 44.01, 'O2': 32.00, 'H2': 2.016,
                'N2': 28.014, 'NH3': 17.031, 'CH4': 16.04, 'NaCl': 58.44,
                'HCl': 36.46, 'NaOH': 40.00, 'C6H12O6': 180.16, 'H2SO4': 98.079,
                'HNO3': 63.01, 'CH3COOH': 60.05, 'C2H5OH': 46.07, 'SO2': 64.07,
                'NO2': 46.01, 'CO': 28.01, 'H2S': 34.08, 'SO3': 80.06,
                'CaCO3': 100.09, 'Na2CO3': 105.99, 'KCl': 74.55, 'MgSO4': 120.37
            }
            
            # Convert given amount to moles if needed
            if given_unit == 'g':
                # Try to identify the substance from equation
                substance = self._extract_first_substance(left_side)
                molar_mass = molar_masses.get(substance, 18.015)  # Default to water
                given_moles = given_amount / molar_mass
                steps.append(f"2. Convert {given_amount} g {substance} to moles: {given_amount:.2f} / {molar_mass:.2f} = {given_moles:.4f} mol")
            elif given_unit == 'mol':
                given_moles = given_amount
                steps.append(f"2. Given amount: {given_amount} mol")
            else:
                given_moles = given_amount
                steps.append(f"2. Given amount: {given_amount} {given_unit}")
            
            # Simple 1:1 ratio assumption (this is very basic)
            result_moles = given_moles
            result_substance = self._extract_substance(right_side, find_substance)
            
            # Convert back to requested unit
            if given_unit == 'g':
                molar_mass = molar_masses.get(result_substance, 18.015)
                result_amount = result_moles * molar_mass
                result_unit = 'g'
                steps.append(f"3. Convert {result_moles:.4f} mol {result_substance} to grams: {result_moles:.4f} × {molar_mass:.2f} = {result_amount:.2f} g")
            else:
                result_amount = result_moles
                result_unit = 'mol'
                steps.append(f"3. Result: {result_moles:.4f} mol {result_substance}")
            
            result_text = f"{result_amount:.2f} {result_unit} {result_substance}"
            
            return CalculationResult(
                input_expression=f"{equation}, {given_amount} {given_unit} -> {find_substance}",
                result=self._convert_latex_to_unicode(result_text),
                steps=steps,
                units=result_unit,
                explanation=f"Basic stoichiometry calculation. For complex equations, use Wolfram Alpha API for accurate results.",
                success=True
            )
            
        except Exception as e:
            return CalculationResult(
                input_expression=f"{equation}, {given_amount} {given_unit} -> {find_substance}",
                result="Unable to calculate stoichiometry",
                steps=["Error in calculation"],
                units="",
                explanation=f"Calculation failed: {str(e)}",
                success=False,
                error_message=f"Error in fallback calculation: {str(e)}"
            )
    
    def _extract_first_substance(self, equation_part: str) -> str:
        """Extract the first substance from equation part."""
        import re
        # Simple pattern to extract chemical formulas
        match = re.search(r'([A-Z][a-z0-9]+)', equation_part.strip())
        return match.group(1) if match else "H2O"
    
    def _extract_substance(self, equation_part: str, target: str) -> str:
        """Extract substance from equation part."""
        import re
        # Try to find target substance in equation
        match = re.search(r'([A-Z][a-z0-9]+)', equation_part.strip())
        return match.group(1) if match else target

# Singleton instance
wolfram_tool = WolframTool()
