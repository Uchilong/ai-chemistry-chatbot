"""PubChem API tool for chemical properties and structural information."""

import pubchempy as pcp
from typing import Dict, List, Optional, Union
import requests
from dataclasses import dataclass

@dataclass
class ChemicalInfo:
    """Data class for chemical information."""
    name: str
    formula: str
    molar_mass: float
    iupac_name: str
    common_name: str
    description: str
    properties: Dict[str, Union[str, float]]
    safety_info: Dict[str, str]

class PubChemTool:
    """Tool for fetching chemical data from PubChem API."""
    
    def __init__(self):
        """Initialize PubChem tool."""
        self.base_url = "https://pubchem.ncbi.nlm.nih.gov/rest/pug"
    
    def get_chemical_info(self, identifier: str) -> Optional[ChemicalInfo]:
        """
        Get comprehensive chemical information.
        
        Args:
            identifier: Chemical name, formula, or CID
            
        Returns:
            ChemicalInfo object or None if not found
        """
        try:
            # Try to get compound by name or CID
            if identifier.isdigit():
                compound = pcp.Compound.from_cid(int(identifier))
            else:
                compound = pcp.get_compounds(identifier, 'name')[0]
            
            # Extract basic information
            info = ChemicalInfo(
                name=compound.iupac_name or identifier,
                formula=compound.molecular_formula,
                molar_mass=compound.molecular_weight,
                iupac_name=compound.iupac_name or "N/A",
                common_name=compound.synonyms[0] if compound.synonyms else identifier,
                description=self._get_description(compound.cid),
                properties=self._get_properties(compound),
                safety_info=self._get_safety_info(compound.cid)
            )
            
            return info
            
        except Exception as e:
            print(f"Error fetching chemical info for {identifier}: {e}")
            return None
    
    def _get_description(self, cid: int) -> str:
        """Get chemical description from PubChem."""
        try:
            url = f"{self.base_url}/compound/cid/{cid}/description/JSON"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                descriptions = data.get('InformationList', {}).get('Information', [])
                if descriptions:
                    return descriptions[0].get('Description', 'No description available')
            return "No description available"
        except:
            return "No description available"
    
    def _get_properties(self, compound) -> Dict[str, Union[str, float]]:
        """Get physical and chemical properties."""
        properties = {}
        
        # Basic properties from pubchempy
        if hasattr(compound, 'molecular_weight'):
            properties['molar_mass'] = compound.molecular_weight
        if hasattr(compound, 'molecular_formula'):
            properties['formula'] = compound.molecular_formula
        if hasattr(compound, 'charge'):
            properties['charge'] = compound.charge
        
        # Additional properties via API call
        try:
            url = f"{self.base_url}/compound/cid/{compound.cid}/property/MeltingPoint,BoilingPoint,Density,FlashPoint/Solubility/JSON"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                props = data.get('PropertyTable', {}).get('Properties', [])
                if props:
                    prop_dict = props[0]
                    properties.update({
                        'melting_point': prop_dict.get('MeltingPoint', 'N/A'),
                        'boiling_point': prop_dict.get('BoilingPoint', 'N/A'),
                        'density': prop_dict.get('Density', 'N/A'),
                        'flash_point': prop_dict.get('FlashPoint', 'N/A'),
                        'solubility': prop_dict.get('Solubility', 'N/A')
                    })
        except:
            pass
        
        return properties
    
    def _get_safety_info(self, cid: int) -> Dict[str, str]:
        """Get safety information."""
        safety = {}
        
        try:
            # Get GHS classification
            url = f"{self.base_url}/compound/cid/{cid}/classification/GHSSignalWord/JSON"
            response = requests.get(url)
            if response.status_code == 200:
                data = response.json()
                classifications = data.get('InformationList', {}).get('Information', [])
                if classifications:
                    safety['signal_word'] = classifications[0].get('Value', 'N/A')
        except:
            safety['signal_word'] = 'N/A'
        
        safety['handling'] = "Use appropriate PPE (gloves, goggles, lab coat)"
        safety['storage'] = "Store in cool, dry place away from incompatible materials"
        
        return safety
    
    def search_compounds(self, query: str, limit: int = 10) -> List[Dict[str, str]]:
        """
        Search for compounds by name or formula.
        
        Args:
            query: Search term
            limit: Maximum number of results
            
        Returns:
            List of compound dictionaries
        """
        try:
            compounds = pcp.get_compounds(query, 'name', listkey='CID')[:limit]
            results = []
            
            for compound in compounds:
                results.append({
                    'cid': compound.cid,
                    'name': compound.iupac_name or query,
                    'formula': compound.molecular_formula,
                    'common_name': compound.synonyms[0] if compound.synonyms else query
                })
            
            return results
            
        except Exception as e:
            print(f"Error searching compounds: {e}")
            return []
    
    def calculate_molar_mass(self, formula: str) -> Optional[float]:
        """
        Calculate molar mass from chemical formula.
        
        Args:
            formula: Chemical formula (e.g., "H2O", "C6H12O6")
            
        Returns:
            Molar mass in g/mol or None if invalid formula
        """
        try:
            compound = pcp.get_compounds(formula, 'formula')
            if compound:
                return compound[0].molecular_weight
            return None
        except:
            return None

# Singleton instance
pubchem_tool = PubChemTool()
