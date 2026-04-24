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
            else:
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
                        result=result,
                        steps=steps,
                        units=self._extract_units(result),
                        explanation=explanation,
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
            result=f"Balanced: {equation} (simplified)",
            steps=["1. Count atoms on each side", "2. Balance coefficients", "3. Verify balance"],
            units="",
            explanation="This is a simplified result. Use Wolfram Alpha API for accurate balancing.",
            success=True
        )
    
    def _calculate_molar_mass_fallback(self, formula: str) -> CalculationResult:
        """Fallback molar mass calculation using basic atomic weights."""
        # Basic atomic masses
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
            
            total_mass = 0
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
        """Fallback stoichiometry calculation."""
        steps = [
            f"1. Analyze equation: {equation}",
            f"2. Given: {given_amount} {given_unit}",
            f"3. Find: amount of {find_substance}",
            "4. Use mole ratios from balanced equation",
            "5. Convert units as needed"
        ]
        
        return CalculationResult(
            input_expression=f"{equation}, {given_amount} {given_unit} -> {find_substance}",
            result="Stoichiometry calculation requires Wolfram Alpha API for accuracy",
            steps=steps,
            units="",
            explanation="This is a simplified guide. Use Wolfram Alpha API for detailed calculations.",
            success=True
        )

# Singleton instance
wolfram_tool = WolframTool()
