"""
Kosher Meal & Diet Preparation Agent
Michael Shapira D1 Pathway - Specialized Agent

Based on Michael Andrew Framework:
- Keto Mon-Thu (strict kosher)
- Moderate carbs Fri-Sun (Shabbat)
- D1 swimmer nutritional requirements
"""

from typing import Dict, List, Any, Optional
from datetime import datetime, date
from dataclasses import dataclass
from enum import Enum


class DayType(Enum):
    KETO = "keto"  # Mon-Thu
    SHABBAT = "shabbat"  # Fri-Sun


class MealType(Enum):
    PRE_PRACTICE = "pre_practice"
    POST_PRACTICE = "post_practice"
    BREAKFAST = "breakfast"
    LUNCH = "lunch"
    DINNER = "dinner"
    SNACK = "snack"
    SHABBAT_DINNER = "shabbat_dinner"


@dataclass
class MacroTargets:
    """Daily macro targets based on day type"""
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    fiber_g: int


@dataclass
class Meal:
    """Individual meal definition"""
    name: str
    meal_type: MealType
    ingredients: List[str]
    calories: int
    protein_g: int
    carbs_g: int
    fat_g: int
    prep_time_min: int
    kosher_notes: str
    is_pareve: bool = False
    is_dairy: bool = False
    is_meat: bool = False


class KosherDietAgent:
    """
    Specialized agent for Michael's kosher D1 swimmer diet.
    Implements Michael Andrew-inspired keto framework adapted for Orthodox observance.
    """
    
    # Michael Andrew-style targets adapted for 16yo swimmer
    KETO_TARGETS = MacroTargets(
        calories=3200,
        protein_g=180,  # High for muscle recovery
        carbs_g=50,     # Strict keto <50g
        fat_g=240,      # Primary fuel source
        fiber_g=25
    )
    
    SHABBAT_TARGETS = MacroTargets(
        calories=3500,  # Higher for glycogen replenishment
        protein_g=180,
        carbs_g=200,    # Moderate carbs allowed
        fat_g=180,
        fiber_g=30
    )
    
    def __init__(self, swimmer_profile: Dict[str, Any]):
        self.swimmer = swimmer_profile
        self.meal_plans: Dict[str, List[Meal]] = {}
        self.shopping_lists: List[Dict] = []
        
    def get_day_type(self, check_date: date = None) -> DayType:
        """Determine if date is keto or Shabbat period"""
        if check_date is None:
            check_date = date.today()
        
        # Friday sunset to Sunday = Shabbat/moderate carbs
        weekday = check_date.weekday()
        if weekday in [4, 5, 6]:  # Fri, Sat, Sun
            return DayType.SHABBAT
        return DayType.KETO
    
    def get_macro_targets(self, check_date: date = None) -> MacroTargets:
        """Get macro targets for given date"""
        day_type = self.get_day_type(check_date)
        if day_type == DayType.SHABBAT:
            return self.SHABBAT_TARGETS
        return self.KETO_TARGETS
    
    def generate_keto_meals(self) -> List[Meal]:
        """Generate keto-compliant kosher meals (Mon-Thu)"""
        meals = [
            # Breakfast
            Meal(
                name="Keto Power Breakfast",
                meal_type=MealType.BREAKFAST,
                ingredients=[
                    "4 eggs (scrambled in olive oil)",
                    "3 slices turkey bacon (kosher)",
                    "1/2 avocado",
                    "Sautéed spinach (2 cups)",
                    "2 tbsp cream cheese"
                ],
                calories=750,
                protein_g=45,
                carbs_g=8,
                fat_g=58,
                prep_time_min=15,
                kosher_notes="Use separate dairy utensils for cream cheese",
                is_dairy=True
            ),
            
            # Pre-Practice
            Meal(
                name="Pre-Practice Fat Bomb",
                meal_type=MealType.PRE_PRACTICE,
                ingredients=[
                    "2 tbsp almond butter",
                    "1 tbsp MCT oil",
                    "1/4 cup macadamia nuts",
                    "Celery sticks (3)"
                ],
                calories=450,
                protein_g=10,
                carbs_g=6,
                fat_g=42,
                prep_time_min=5,
                kosher_notes="Pareve - can eat with any meal",
                is_pareve=True
            ),
            
            # Post-Practice
            Meal(
                name="Recovery Protein Shake",
                meal_type=MealType.POST_PRACTICE,
                ingredients=[
                    "Kosher whey protein (2 scoops)",
                    "1 cup unsweetened almond milk",
                    "1 tbsp MCT oil",
                    "1/4 avocado",
                    "Ice"
                ],
                calories=400,
                protein_g=50,
                carbs_g=5,
                fat_g=20,
                prep_time_min=5,
                kosher_notes="Check protein powder for kosher certification (OU/OK)",
                is_dairy=True
            ),
            
            # Lunch
            Meal(
                name="Grilled Salmon Power Bowl",
                meal_type=MealType.LUNCH,
                ingredients=[
                    "8oz wild salmon fillet",
                    "2 cups mixed greens",
                    "1/2 avocado",
                    "2 tbsp olive oil dressing",
                    "1/4 cup olives",
                    "Cherry tomatoes (5)"
                ],
                calories=700,
                protein_g=55,
                carbs_g=10,
                fat_g=50,
                prep_time_min=20,
                kosher_notes="Salmon is inherently kosher, check for scales",
                is_pareve=True
            ),
            
            # Dinner
            Meal(
                name="Ribeye Steak with Vegetables",
                meal_type=MealType.DINNER,
                ingredients=[
                    "12oz kosher ribeye steak",
                    "Roasted broccoli (2 cups)",
                    "Cauliflower mash (1 cup)",
                    "2 tbsp ghee",
                    "Garlic herb butter"
                ],
                calories=900,
                protein_g=70,
                carbs_g=15,
                fat_g=65,
                prep_time_min=30,
                kosher_notes="Meat meal - wait 6 hours before dairy",
                is_meat=True
            ),
            
            # Evening Snack
            Meal(
                name="Keto Night Snack",
                meal_type=MealType.SNACK,
                ingredients=[
                    "String cheese (2)",
                    "Almonds (1/4 cup)",
                    "Sugar-free jello"
                ],
                calories=300,
                protein_g=15,
                carbs_g=4,
                fat_g=25,
                prep_time_min=2,
                kosher_notes="Check jello for kosher gelatin",
                is_dairy=True
            )
        ]
        return meals
    
    def generate_shabbat_meals(self) -> List[Meal]:
        """Generate Shabbat-appropriate meals with moderate carbs (Fri-Sun)"""
        meals = [
            # Friday Night Shabbat Dinner
            Meal(
                name="Traditional Shabbat Dinner",
                meal_type=MealType.SHABBAT_DINNER,
                ingredients=[
                    "Challah (2 slices)",
                    "Chicken soup with matzo ball",
                    "Roasted chicken thighs (2)",
                    "Roasted potatoes (1 cup)",
                    "Glazed carrots",
                    "Israeli salad"
                ],
                calories=1100,
                protein_g=60,
                carbs_g=80,
                fat_g=55,
                prep_time_min=120,
                kosher_notes="Full meat meal - prepare before Shabbat",
                is_meat=True
            ),
            
            # Saturday Lunch
            Meal(
                name="Shabbat Lunch Cholent",
                meal_type=MealType.LUNCH,
                ingredients=[
                    "Cholent (beef, beans, barley, potatoes)",
                    "Challah (1 slice)",
                    "Hummus with vegetables",
                    "Pickles"
                ],
                calories=850,
                protein_g=45,
                carbs_g=60,
                fat_g=45,
                prep_time_min=0,  # Prepared before Shabbat
                kosher_notes="Slow-cooked from Friday - kept warm on plata",
                is_meat=True
            ),
            
            # Sunday Recovery Breakfast
            Meal(
                name="Carb-Up Breakfast",
                meal_type=MealType.BREAKFAST,
                ingredients=[
                    "Oatmeal (1 cup cooked)",
                    "4 eggs",
                    "Whole wheat toast (2 slices)",
                    "Orange juice (1 cup)",
                    "Greek yogurt (1 cup)"
                ],
                calories=900,
                protein_g=50,
                carbs_g=85,
                fat_g=35,
                prep_time_min=20,
                kosher_notes="Dairy meal - good for glycogen replenishment",
                is_dairy=True
            )
        ]
        return meals
    
    def generate_weekly_plan(self) -> Dict[str, List[Meal]]:
        """Generate full weekly meal plan"""
        plan = {
            "monday": self.generate_keto_meals(),
            "tuesday": self.generate_keto_meals(),
            "wednesday": self.generate_keto_meals(),
            "thursday": self.generate_keto_meals(),
            "friday": self._friday_transition_meals(),
            "saturday": self.generate_shabbat_meals(),
            "sunday": self._sunday_transition_meals()
        }
        self.meal_plans = plan
        return plan
    
    def _friday_transition_meals(self) -> List[Meal]:
        """Friday: Keto during day, Shabbat dinner"""
        day_meals = self.generate_keto_meals()[:4]  # Breakfast through dinner prep
        shabbat_dinner = self.generate_shabbat_meals()[0]  # Add Shabbat dinner
        day_meals.append(shabbat_dinner)
        return day_meals
    
    def _sunday_transition_meals(self) -> List[Meal]:
        """Sunday: Moderate carbs, transition back to keto"""
        return [
            self.generate_shabbat_meals()[2],  # Carb-up breakfast
            self.generate_keto_meals()[1],      # Pre-practice
            self.generate_keto_meals()[2],      # Post-practice
            self.generate_keto_meals()[3],      # Lunch
            self.generate_keto_meals()[4],      # Dinner (back to keto)
        ]
    
    def generate_shopping_list(self, week_start: date = None) -> Dict[str, List[str]]:
        """Generate weekly shopping list by category"""
        shopping = {
            "proteins_meat": [
                "Kosher ribeye steaks (3 lbs)",
                "Kosher chicken thighs (4 lbs)",
                "Turkey bacon (2 packs, kosher)",
                "Beef for cholent (2 lbs)",
                "Wild salmon fillets (2 lbs)"
            ],
            "proteins_dairy": [
                "Eggs (3 dozen)",
                "Kosher whey protein (2 lb tub)",
                "String cheese (2 packs)",
                "Cream cheese (2 blocks)",
                "Greek yogurt (large container)",
                "Butter (2 lbs)"
            ],
            "fats_oils": [
                "MCT oil (16 oz)",
                "Extra virgin olive oil",
                "Ghee (kosher)",
                "Almond butter (2 jars)",
                "Macadamia nuts (1 lb)",
                "Almonds (1 lb)"
            ],
            "vegetables": [
                "Avocados (10)",
                "Spinach (2 large bags)",
                "Broccoli (4 heads)",
                "Cauliflower (3 heads)",
                "Mixed greens (2 containers)",
                "Celery (2 bunches)",
                "Cherry tomatoes (2 pints)",
                "Olives (2 jars)",
                "Carrots (2 lbs)",
                "Potatoes (5 lbs - Shabbat)"
            ],
            "shabbat_items": [
                "Challah (2 loaves)",
                "Matzo meal (for matzo balls)",
                "Barley (for cholent)",
                "Beans (for cholent)",
                "Honey (for glazing)"
            ],
            "beverages_misc": [
                "Unsweetened almond milk (2 cartons)",
                "Sugar-free jello mix",
                "Orange juice (Shabbat only)",
                "Sparkling water"
            ]
        }
        return shopping
    
    def calculate_daily_macros(self, meals: List[Meal]) -> Dict[str, int]:
        """Calculate total macros for a day's meals"""
        totals = {
            "calories": sum(m.calories for m in meals),
            "protein_g": sum(m.protein_g for m in meals),
            "carbs_g": sum(m.carbs_g for m in meals),
            "fat_g": sum(m.fat_g for m in meals)
        }
        return totals
    
    def get_travel_meal_options(self, destination: str) -> List[Dict]:
        """Get kosher meal options for school visits"""
        # Common D1 school locations with kosher options
        kosher_options = {
            "gainesville": [
                {"name": "Chabad UF Daily Lunch", "type": "meat", "address": "2021 NW 5th Ave"},
                {"name": "Krishna Lunch (vegetarian)", "type": "pareve", "address": "Plaza of Americas"},
                {"name": "Publix Kosher Section", "type": "grocery", "address": "Multiple locations"}
            ],
            "tallahassee": [
                {"name": "Chabad FSU", "type": "meat", "address": "519 Copeland St"},
                {"name": "Whole Foods (kosher section)", "type": "grocery", "address": "1817 Thomasville Rd"}
            ],
            "tampa": [
                {"name": "Maccabi's Kosher Deli", "type": "meat", "address": "12551 N Dale Mabry"},
                {"name": "Chabad USF", "type": "meat", "address": "13287 Arbor Pointe Dr"}
            ],
            "miami": [
                {"name": "Multiple kosher restaurants", "type": "meat/dairy", "address": "Miami Beach area"},
                {"name": "Chabad UM", "type": "meat", "address": "1501 Brescia Ave"}
            ]
        }
        
        dest_key = destination.lower().replace(" ", "")
        return kosher_options.get(dest_key, [])
    
    def get_meet_day_nutrition(self, events: List[str], event_times: List[str]) -> Dict:
        """Generate nutrition plan for competition day"""
        return {
            "morning": {
                "meal": "Light keto breakfast",
                "timing": "3 hours before first event",
                "items": ["2 eggs", "1/2 avocado", "MCT coffee"],
                "calories": 450
            },
            "between_events": {
                "timing": "20-30 min after each event",
                "items": ["Protein shake", "Handful almonds"],
                "notes": "Small amounts, easy to digest"
            },
            "post_competition": {
                "timing": "Within 30 minutes of final event",
                "items": ["Full protein shake", "Keto snack pack"],
                "notes": "Prioritize protein for recovery"
            },
            "dinner": {
                "timing": "2-3 hours post-competition",
                "items": ["Full keto dinner", "Extra protein"],
                "notes": "Can be slightly higher carb if Shabbat"
            }
        }


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    print("🥗 Kosher Diet Agent - Michael Shapira D1 Pathway")
    print("=" * 50)
    
    profile = {
        "name": "Michael Shapira",
        "age": 16,
        "weight_lbs": 165,
        "height_inches": 70,
        "events": ["50 Free", "100 Free", "100 Fly", "100 Back"]
    }
    
    agent = KosherDietAgent(profile)
    
    # Check today's day type
    day_type = agent.get_day_type()
    targets = agent.get_macro_targets()
    
    print(f"\n📅 Today is: {day_type.value.upper()} day")
    print(f"🎯 Macro Targets:")
    print(f"   Calories: {targets.calories}")
    print(f"   Protein: {targets.protein_g}g")
    print(f"   Carbs: {targets.carbs_g}g")
    print(f"   Fat: {targets.fat_g}g")
    
    # Generate sample meals
    if day_type == DayType.KETO:
        meals = agent.generate_keto_meals()
    else:
        meals = agent.generate_shabbat_meals()
    
    print(f"\n🍽️ Today's Meals ({len(meals)}):")
    for meal in meals[:3]:
        print(f"   • {meal.name} ({meal.calories} cal, {meal.protein_g}g protein)")
    
    # Shopping list preview
    shopping = agent.generate_shopping_list()
    print(f"\n🛒 Shopping List Categories: {len(shopping)}")
    for category in list(shopping.keys())[:3]:
        print(f"   • {category}: {len(shopping[category])} items")
    
    print("\n✅ Kosher Diet Agent initialized")
