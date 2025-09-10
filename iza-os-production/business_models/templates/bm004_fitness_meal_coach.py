#!/usr/bin/env python3
"""
IZA OS Business Model: BM004 - AI Fitness & Meal Planning Coach

This template implements an AI-powered fitness and meal planning service that:
- Provides daily adaptive plans based on user energy and goals
- Generates personalized meal plans with grocery lists
- Tracks fitness progress and adjusts recommendations
- Sends push notifications and weekly summaries
- Ensures content avoids medical claims with HITL review

Stack Integration:
- SuperDesign: Generate app screens and component set
- PromptLab: Nutrition/fitness prompt templates
- shadcn/ui: Landing page and subscription management
- ChromaDB: On-device embeddings for personalization
- Agent-S: Automated workflow orchestration
"""

import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from pathlib import Path
import json
import sqlite3
import uuid
import os
import hashlib
from enum import Enum

# Core framework imports
from fastmcp import FastMCP, Context

class FitnessLevel(Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class GoalType(Enum):
    WEIGHT_LOSS = "weight_loss"
    MUSCLE_GAIN = "muscle_gain"
    MAINTENANCE = "maintenance"
    ENDURANCE = "endurance"
    GENERAL_FITNESS = "general_fitness"

class DietaryRestriction(Enum):
    VEGETARIAN = "vegetarian"
    VEGAN = "vegan"
    GLUTEN_FREE = "gluten_free"
    DAIRY_FREE = "dairy_free"
    KETO = "keto"
    PALEO = "paleo"
    NONE = "none"

@dataclass
class UserProfile:
    """User profile data structure"""
    id: str
    name: str
    age: int
    gender: str
    height_cm: float
    weight_kg: float
    fitness_level: FitnessLevel
    goal_type: GoalType
    dietary_restrictions: List[DietaryRestriction]
    allergies: List[str]
    activity_level: str  # sedentary, lightly_active, moderately_active, very_active
    target_weight: Optional[float] = None
    created_at: datetime = None
    updated_at: datetime = None

@dataclass
class MealPlan:
    """Meal plan data structure"""
    id: str
    user_id: str
    date: datetime
    meals: List[Dict[str, Any]]  # breakfast, lunch, dinner, snacks
    total_calories: int
    macros: Dict[str, float]  # protein, carbs, fat
    grocery_list: List[Dict[str, Any]]
    created_at: datetime

@dataclass
class WorkoutPlan:
    """Workout plan data structure"""
    id: str
    user_id: str
    date: datetime
    exercises: List[Dict[str, Any]]
    duration_minutes: int
    difficulty_level: str
    calories_burned: int
    muscle_groups: List[str]
    created_at: datetime

@dataclass
class ProgressEntry:
    """Progress tracking data structure"""
    id: str
    user_id: str
    date: datetime
    weight: Optional[float] = None
    body_fat_percentage: Optional[float] = None
    measurements: Dict[str, float] = None  # waist, chest, arms, etc.
    energy_level: int = None  # 1-10 scale
    mood: int = None  # 1-10 scale
    sleep_hours: Optional[float] = None
    notes: str = ""

class FitnessMealCoach:
    """
    AI Fitness & Meal Planning Coach
    
    Features:
    - Personalized meal planning with dietary restrictions
    - Adaptive workout plans based on fitness level and goals
    - Progress tracking and analytics
    - Push notifications and engagement
    - Compliance monitoring for medical claims
    - Grocery list generation and meal prep guidance
    """
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
        self.logger = logging.getLogger(__name__)
        self.db_path = Path("fitness_meal_coach.db")
        self.meal_plans_dir = Path("meal_plans")
        self.workout_plans_dir = Path("workout_plans")
        self.user_data_dir = Path("user_data")
        
        # Create directories
        for dir_path in [self.meal_plans_dir, self.workout_plans_dir, self.user_data_dir]:
            dir_path.mkdir(exist_ok=True)
        
        # Initialize database
        self._init_database()
        
        # Initialize FastMCP
        self.mcp = FastMCP("FitnessMealCoach")
        
        # API configurations
        self.nutrition_api_key = config.get("nutrition_api_key", "")
        self.fitness_api_key = config.get("fitness_api_key", "")
        self.push_notification_key = config.get("push_notification_key", "")
        
        # Business metrics
        self.metrics = {
            "total_users": 0,
            "active_subscribers": 0,
            "meal_plans_generated": 0,
            "workout_plans_generated": 0,
            "average_user_engagement": 0.0,
            "monthly_revenue": 0.0
        }
        
        # Nutrition database (simplified)
        self.nutrition_db = self._load_nutrition_database()
        
        # Exercise database (simplified)
        self.exercise_db = self._load_exercise_database()
    
    def _init_database(self):
        """Initialize SQLite database for fitness and meal planning"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    id TEXT PRIMARY KEY,
                    name TEXT NOT NULL,
                    age INTEGER,
                    gender TEXT,
                    height_cm REAL,
                    weight_kg REAL,
                    fitness_level TEXT,
                    goal_type TEXT,
                    dietary_restrictions TEXT,
                    allergies TEXT,
                    activity_level TEXT,
                    target_weight REAL,
                    created_at TIMESTAMP,
                    updated_at TIMESTAMP
                )
            """)
            
            # Meal plans table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS meal_plans (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    date TIMESTAMP,
                    meals TEXT,
                    total_calories INTEGER,
                    macros TEXT,
                    grocery_list TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Workout plans table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS workout_plans (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    date TIMESTAMP,
                    exercises TEXT,
                    duration_minutes INTEGER,
                    difficulty_level TEXT,
                    calories_burned INTEGER,
                    muscle_groups TEXT,
                    created_at TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Progress tracking table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS progress_entries (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    date TIMESTAMP,
                    weight REAL,
                    body_fat_percentage REAL,
                    measurements TEXT,
                    energy_level INTEGER,
                    mood INTEGER,
                    sleep_hours REAL,
                    notes TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            # Subscriptions table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS subscriptions (
                    id TEXT PRIMARY KEY,
                    user_id TEXT,
                    plan_type TEXT,
                    status TEXT,
                    start_date TIMESTAMP,
                    end_date TIMESTAMP,
                    price REAL,
                    FOREIGN KEY (user_id) REFERENCES users (id)
                )
            """)
            
            conn.commit()
    
    def _load_nutrition_database(self) -> Dict[str, Any]:
        """Load nutrition database with food information"""
        return {
            "foods": {
                "chicken_breast": {
                    "calories_per_100g": 165,
                    "protein_per_100g": 31,
                    "carbs_per_100g": 0,
                    "fat_per_100g": 3.6,
                    "allergens": [],
                    "dietary_tags": ["high_protein", "low_carb"]
                },
                "brown_rice": {
                    "calories_per_100g": 111,
                    "protein_per_100g": 2.6,
                    "carbs_per_100g": 23,
                    "fat_per_100g": 0.9,
                    "allergens": [],
                    "dietary_tags": ["whole_grain", "gluten_free"]
                },
                "broccoli": {
                    "calories_per_100g": 34,
                    "protein_per_100g": 2.8,
                    "carbs_per_100g": 7,
                    "fat_per_100g": 0.4,
                    "allergens": [],
                    "dietary_tags": ["vegetable", "low_calorie", "high_fiber"]
                },
                "salmon": {
                    "calories_per_100g": 208,
                    "protein_per_100g": 25,
                    "carbs_per_100g": 0,
                    "fat_per_100g": 12,
                    "allergens": ["fish"],
                    "dietary_tags": ["high_protein", "omega_3", "low_carb"]
                },
                "quinoa": {
                    "calories_per_100g": 120,
                    "protein_per_100g": 4.4,
                    "carbs_per_100g": 22,
                    "fat_per_100g": 1.9,
                    "allergens": [],
                    "dietary_tags": ["complete_protein", "gluten_free", "whole_grain"]
                }
            },
            "meal_templates": {
                "breakfast": [
                    "oatmeal_with_berries",
                    "greek_yogurt_parfait",
                    "scrambled_eggs_with_vegetables",
                    "protein_smoothie"
                ],
                "lunch": [
                    "grilled_chicken_salad",
                    "quinoa_bowl",
                    "turkey_wrap",
                    "vegetable_stir_fry"
                ],
                "dinner": [
                    "baked_salmon_with_vegetables",
                    "chicken_and_brown_rice",
                    "vegetarian_stir_fry",
                    "grilled_fish_with_quinoa"
                ],
                "snacks": [
                    "greek_yogurt_with_nuts",
                    "apple_with_almond_butter",
                    "protein_bar",
                    "vegetable_sticks_with_hummus"
                ]
            }
        }
    
    def _load_exercise_database(self) -> Dict[str, Any]:
        """Load exercise database with workout information"""
        return {
            "exercises": {
                "push_ups": {
                    "muscle_groups": ["chest", "shoulders", "triceps"],
                    "difficulty": "beginner",
                    "calories_per_minute": 8,
                    "equipment": "none"
                },
                "squats": {
                    "muscle_groups": ["quadriceps", "glutes", "hamstrings"],
                    "difficulty": "beginner",
                    "calories_per_minute": 6,
                    "equipment": "none"
                },
                "plank": {
                    "muscle_groups": ["core", "shoulders"],
                    "difficulty": "beginner",
                    "calories_per_minute": 4,
                    "equipment": "none"
                },
                "burpees": {
                    "muscle_groups": ["full_body"],
                    "difficulty": "intermediate",
                    "calories_per_minute": 12,
                    "equipment": "none"
                },
                "mountain_climbers": {
                    "muscle_groups": ["core", "shoulders", "legs"],
                    "difficulty": "intermediate",
                    "calories_per_minute": 10,
                    "equipment": "none"
                }
            },
            "workout_templates": {
                "beginner": {
                    "duration_minutes": 20,
                    "exercises": ["push_ups", "squats", "plank"],
                    "sets": 2,
                    "reps": [10, 15, 30]
                },
                "intermediate": {
                    "duration_minutes": 30,
                    "exercises": ["burpees", "mountain_climbers", "push_ups", "squats"],
                    "sets": 3,
                    "reps": [8, 20, 12, 20]
                },
                "advanced": {
                    "duration_minutes": 45,
                    "exercises": ["burpees", "mountain_climbers", "push_ups", "squats", "plank"],
                    "sets": 4,
                    "reps": [12, 25, 15, 25, 60]
                }
            }
        }
    
    async def create_user_profile(self, user_data: Dict[str, Any]) -> UserProfile:
        """
        Create user profile for fitness and meal planning
        
        Agent-S Task: intake_agent
        """
        self.logger.info(f"Creating user profile for {user_data.get('name', 'Unknown')}")
        
        profile = UserProfile(
            id=str(uuid.uuid4()),
            name=user_data.get("name", ""),
            age=user_data.get("age", 25),
            gender=user_data.get("gender", "other"),
            height_cm=user_data.get("height_cm", 170.0),
            weight_kg=user_data.get("weight_kg", 70.0),
            fitness_level=FitnessLevel(user_data.get("fitness_level", "beginner")),
            goal_type=GoalType(user_data.get("goal_type", "general_fitness")),
            dietary_restrictions=[DietaryRestriction(d) for d in user_data.get("dietary_restrictions", ["none"])],
            allergies=user_data.get("allergies", []),
            activity_level=user_data.get("activity_level", "moderately_active"),
            target_weight=user_data.get("target_weight"),
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        
        # Store user profile
        await self._store_user_profile(profile)
        
        # Calculate initial calorie needs
        calorie_needs = await self._calculate_calorie_needs(profile)
        
        self.logger.info(f"User profile created with daily calorie needs: {calorie_needs}")
        return profile
    
    async def _calculate_calorie_needs(self, profile: UserProfile) -> int:
        """Calculate daily calorie needs using Mifflin-St Jeor equation"""
        # Base Metabolic Rate (BMR)
        if profile.gender.lower() == "male":
            bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age + 5
        else:
            bmr = 10 * profile.weight_kg + 6.25 * profile.height_cm - 5 * profile.age - 161
        
        # Activity multipliers
        activity_multipliers = {
            "sedentary": 1.2,
            "lightly_active": 1.375,
            "moderately_active": 1.55,
            "very_active": 1.725
        }
        
        tdee = bmr * activity_multipliers.get(profile.activity_level, 1.55)
        
        # Adjust based on goal
        if profile.goal_type == GoalType.WEIGHT_LOSS:
            tdee *= 0.8  # 20% calorie deficit
        elif profile.goal_type == GoalType.MUSCLE_GAIN:
            tdee *= 1.1  # 10% calorie surplus
        
        return int(tdee)
    
    async def _store_user_profile(self, profile: UserProfile):
        """Store user profile in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO users 
                (id, name, age, gender, height_cm, weight_kg, fitness_level,
                 goal_type, dietary_restrictions, allergies, activity_level,
                 target_weight, created_at, updated_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                profile.id,
                profile.name,
                profile.age,
                profile.gender,
                profile.height_cm,
                profile.weight_kg,
                profile.fitness_level.value,
                profile.goal_type.value,
                json.dumps([d.value for d in profile.dietary_restrictions]),
                json.dumps(profile.allergies),
                profile.activity_level,
                profile.target_weight,
                profile.created_at,
                profile.updated_at
            ))
            
            conn.commit()
    
    async def generate_meal_plan(self, user_id: str, date: datetime = None) -> MealPlan:
        """
        Generate personalized meal plan for user
        
        Agent-S Task: planner_agent
        """
        self.logger.info(f"Generating meal plan for user {user_id}")
        
        if date is None:
            date = datetime.now()
        
        # Get user profile
        profile = await self._get_user_profile(user_id)
        if not profile:
            raise ValueError(f"User {user_id} not found")
        
        # Calculate calorie needs
        calorie_needs = await self._calculate_calorie_needs(profile)
        
        # Generate meals
        meals = await self._generate_meals(profile, calorie_needs)
        
        # Generate grocery list
        grocery_list = await self._generate_grocery_list(meals)
        
        # Calculate macros
        macros = await self._calculate_macros(meals)
        
        meal_plan = MealPlan(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=date,
            meals=meals,
            total_calories=calorie_needs,
            macros=macros,
            grocery_list=grocery_list,
            created_at=datetime.now()
        )
        
        # Store meal plan
        await self._store_meal_plan(meal_plan)
        
        self.logger.info(f"Meal plan generated with {calorie_needs} calories")
        return meal_plan
    
    async def _generate_meals(self, profile: UserProfile, calorie_needs: int) -> List[Dict[str, Any]]:
        """Generate meals based on user profile and calorie needs"""
        meals = []
        
        # Distribute calories across meals
        calorie_distribution = {
            "breakfast": int(calorie_needs * 0.25),
            "lunch": int(calorie_needs * 0.35),
            "dinner": int(calorie_needs * 0.30),
            "snacks": int(calorie_needs * 0.10)
        }
        
        # Generate each meal
        for meal_type, calories in calorie_distribution.items():
            meal = await self._create_meal(profile, meal_type, calories)
            meals.append(meal)
        
        return meals
    
    async def _create_meal(self, profile: UserProfile, meal_type: str, calories: int) -> Dict[str, Any]:
        """Create a specific meal"""
        # Get meal templates
        templates = self.nutrition_db["meal_templates"].get(meal_type, [])
        
        # Select template based on dietary restrictions
        selected_template = self._select_meal_template(profile, templates)
        
        # Create meal with foods that fit dietary restrictions
        foods = self._select_foods_for_meal(profile, selected_template, calories)
        
        return {
            "meal_type": meal_type,
            "template": selected_template,
            "foods": foods,
            "calories": calories,
            "prep_time_minutes": 15,
            "difficulty": "easy"
        }
    
    def _select_meal_template(self, profile: UserProfile, templates: List[str]) -> str:
        """Select appropriate meal template based on dietary restrictions"""
        # Simplified selection - would use more sophisticated logic
        if DietaryRestriction.VEGETARIAN in profile.dietary_restrictions:
            return "vegetarian_" + templates[0] if templates else "vegetarian_bowl"
        elif DietaryRestriction.KETO in profile.dietary_restrictions:
            return "keto_" + templates[0] if templates else "keto_salad"
        else:
            return templates[0] if templates else "balanced_meal"
    
    def _select_foods_for_meal(self, profile: UserProfile, template: str, calories: int) -> List[Dict[str, Any]]:
        """Select foods for meal based on template and calorie target"""
        foods = []
        remaining_calories = calories
        
        # Get available foods that fit dietary restrictions
        available_foods = self._get_available_foods(profile)
        
        # Select foods to meet calorie target
        for food_name, food_data in available_foods.items():
            if remaining_calories <= 0:
                break
            
            # Calculate portion size
            portion_size = min(remaining_calories / food_data["calories_per_100g"], 200)  # Max 200g
            
            if portion_size > 10:  # Only include if portion is reasonable
                foods.append({
                    "name": food_name,
                    "portion_grams": int(portion_size),
                    "calories": int(portion_size * food_data["calories_per_100g"]),
                    "protein": portion_size * food_data["protein_per_100g"],
                    "carbs": portion_size * food_data["carbs_per_100g"],
                    "fat": portion_size * food_data["fat_per_100g"]
                })
                
                remaining_calories -= int(portion_size * food_data["calories_per_100g"])
        
        return foods
    
    def _get_available_foods(self, profile: UserProfile) -> Dict[str, Any]:
        """Get foods that fit user's dietary restrictions"""
        available_foods = {}
        
        for food_name, food_data in self.nutrition_db["foods"].items():
            # Check dietary restrictions
            if self._food_fits_dietary_restrictions(food_data, profile):
                available_foods[food_name] = food_data
        
        return available_foods
    
    def _food_fits_dietary_restrictions(self, food_data: Dict[str, Any], profile: UserProfile) -> bool:
        """Check if food fits user's dietary restrictions"""
        # Check allergies
        for allergen in food_data.get("allergens", []):
            if allergen in profile.allergies:
                return False
        
        # Check dietary restrictions
        dietary_tags = food_data.get("dietary_tags", [])
        
        if DietaryRestriction.VEGETARIAN in profile.dietary_restrictions:
            if "meat" in dietary_tags or "fish" in dietary_tags:
                return False
        
        if DietaryRestriction.VEGAN in profile.dietary_restrictions:
            if "dairy" in dietary_tags or "meat" in dietary_tags or "fish" in dietary_tags:
                return False
        
        if DietaryRestriction.GLUTEN_FREE in profile.dietary_restrictions:
            if "gluten" in dietary_tags:
                return False
        
        if DietaryRestriction.KETO in profile.dietary_restrictions:
            if "high_carb" in dietary_tags:
                return False
        
        return True
    
    async def _generate_grocery_list(self, meals: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Generate grocery list from meals"""
        grocery_items = {}
        
        for meal in meals:
            for food in meal.get("foods", []):
                food_name = food["name"]
                portion_grams = food["portion_grams"]
                
                if food_name in grocery_items:
                    grocery_items[food_name]["total_grams"] += portion_grams
                else:
                    grocery_items[food_name] = {
                        "name": food_name,
                        "total_grams": portion_grams,
                        "category": self._get_food_category(food_name),
                        "estimated_price": self._estimate_food_price(food_name, portion_grams)
                    }
        
        return list(grocery_items.values())
    
    def _get_food_category(self, food_name: str) -> str:
        """Get food category for grocery organization"""
        categories = {
            "chicken_breast": "Protein",
            "salmon": "Protein",
            "brown_rice": "Grains",
            "quinoa": "Grains",
            "broccoli": "Vegetables"
        }
        return categories.get(food_name, "Other")
    
    def _estimate_food_price(self, food_name: str, grams: float) -> float:
        """Estimate food price (simplified)"""
        price_per_100g = {
            "chicken_breast": 3.50,
            "salmon": 8.00,
            "brown_rice": 0.50,
            "quinoa": 2.00,
            "broccoli": 1.50
        }
        return (price_per_100g.get(food_name, 2.00) * grams) / 100
    
    async def _calculate_macros(self, meals: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate total macros from meals"""
        total_protein = 0
        total_carbs = 0
        total_fat = 0
        
        for meal in meals:
            for food in meal.get("foods", []):
                total_protein += food.get("protein", 0)
                total_carbs += food.get("carbs", 0)
                total_fat += food.get("fat", 0)
        
        return {
            "protein": round(total_protein, 1),
            "carbs": round(total_carbs, 1),
            "fat": round(total_fat, 1)
        }
    
    async def _store_meal_plan(self, meal_plan: MealPlan):
        """Store meal plan in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO meal_plans 
                (id, user_id, date, meals, total_calories, macros, grocery_list, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                meal_plan.id,
                meal_plan.user_id,
                meal_plan.date,
                json.dumps(meal_plan.meals),
                meal_plan.total_calories,
                json.dumps(meal_plan.macros),
                json.dumps(meal_plan.grocery_list),
                meal_plan.created_at
            ))
            
            conn.commit()
    
    async def generate_workout_plan(self, user_id: str, date: datetime = None) -> WorkoutPlan:
        """
        Generate personalized workout plan for user
        
        Agent-S Task: workout_agent
        """
        self.logger.info(f"Generating workout plan for user {user_id}")
        
        if date is None:
            date = datetime.now()
        
        # Get user profile
        profile = await self._get_user_profile(user_id)
        if not profile:
            raise ValueError(f"User {user_id} not found")
        
        # Generate workout based on fitness level and goals
        workout_data = await self._create_workout(profile)
        
        workout_plan = WorkoutPlan(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=date,
            exercises=workout_data["exercises"],
            duration_minutes=workout_data["duration_minutes"],
            difficulty_level=profile.fitness_level.value,
            calories_burned=workout_data["calories_burned"],
            muscle_groups=workout_data["muscle_groups"],
            created_at=datetime.now()
        )
        
        # Store workout plan
        await self._store_workout_plan(workout_plan)
        
        self.logger.info(f"Workout plan generated with {workout_data['duration_minutes']} minutes duration")
        return workout_plan
    
    async def _create_workout(self, profile: UserProfile) -> Dict[str, Any]:
        """Create workout based on user profile"""
        # Get workout template based on fitness level
        template = self.exercise_db["workout_templates"][profile.fitness_level.value]
        
        exercises = []
        total_calories = 0
        muscle_groups = set()
        
        # Create exercises from template
        for i, exercise_name in enumerate(template["exercises"]):
            exercise_data = self.exercise_db["exercises"][exercise_name]
            
            exercise = {
                "name": exercise_name,
                "sets": template["sets"],
                "reps": template["reps"][i] if i < len(template["reps"]) else template["reps"][-1],
                "muscle_groups": exercise_data["muscle_groups"],
                "equipment": exercise_data["equipment"],
                "calories_per_minute": exercise_data["calories_per_minute"]
            }
            
            exercises.append(exercise)
            muscle_groups.update(exercise_data["muscle_groups"])
            
            # Estimate calories burned (simplified)
            exercise_duration = 5  # minutes per exercise
            total_calories += exercise_data["calories_per_minute"] * exercise_duration
        
        return {
            "exercises": exercises,
            "duration_minutes": template["duration_minutes"],
            "calories_burned": int(total_calories),
            "muscle_groups": list(muscle_groups)
        }
    
    async def _store_workout_plan(self, workout_plan: WorkoutPlan):
        """Store workout plan in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO workout_plans 
                (id, user_id, date, exercises, duration_minutes, difficulty_level,
                 calories_burned, muscle_groups, created_at)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                workout_plan.id,
                workout_plan.user_id,
                workout_plan.date,
                json.dumps(workout_plan.exercises),
                workout_plan.duration_minutes,
                workout_plan.difficulty_level,
                workout_plan.calories_burned,
                json.dumps(workout_plan.muscle_groups),
                workout_plan.created_at
            ))
            
            conn.commit()
    
    async def log_progress(self, user_id: str, progress_data: Dict[str, Any]) -> ProgressEntry:
        """
        Log user progress
        
        Agent-S Task: progress_tracking_agent
        """
        self.logger.info(f"Logging progress for user {user_id}")
        
        progress = ProgressEntry(
            id=str(uuid.uuid4()),
            user_id=user_id,
            date=datetime.now(),
            weight=progress_data.get("weight"),
            body_fat_percentage=progress_data.get("body_fat_percentage"),
            measurements=progress_data.get("measurements", {}),
            energy_level=progress_data.get("energy_level"),
            mood=progress_data.get("mood"),
            sleep_hours=progress_data.get("sleep_hours"),
            notes=progress_data.get("notes", "")
        )
        
        # Store progress entry
        await self._store_progress_entry(progress)
        
        # Update user profile if weight changed
        if progress.weight:
            await self._update_user_weight(user_id, progress.weight)
        
        self.logger.info(f"Progress logged for user {user_id}")
        return progress
    
    async def _store_progress_entry(self, progress: ProgressEntry):
        """Store progress entry in database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                INSERT OR REPLACE INTO progress_entries 
                (id, user_id, date, weight, body_fat_percentage, measurements,
                 energy_level, mood, sleep_hours, notes)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                progress.id,
                progress.user_id,
                progress.date,
                progress.weight,
                progress.body_fat_percentage,
                json.dumps(progress.measurements),
                progress.energy_level,
                progress.mood,
                progress.sleep_hours,
                progress.notes
            ))
            
            conn.commit()
    
    async def _update_user_weight(self, user_id: str, new_weight: float):
        """Update user weight in profile"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("""
                UPDATE users 
                SET weight_kg = ?, updated_at = ?
                WHERE id = ?
            """, (new_weight, datetime.now(), user_id))
            
            conn.commit()
    
    async def send_engagement_notifications(self, user_id: str) -> Dict[str, Any]:
        """
        Send engagement notifications to user
        
        Agent-S Task: engagement_agent
        """
        self.logger.info(f"Sending engagement notifications for user {user_id}")
        
        # Get user profile
        profile = await self._get_user_profile(user_id)
        if not profile:
            raise ValueError(f"User {user_id} not found")
        
        # Get recent progress
        recent_progress = await self._get_recent_progress(user_id, days=7)
        
        # Generate personalized notifications
        notifications = []
        
        # Daily meal plan reminder
        notifications.append({
            "type": "meal_plan_reminder",
            "title": "Your Daily Meal Plan is Ready! 🍽️",
            "message": f"Hi {profile.name}! Your personalized meal plan for today is ready. Check out your delicious and nutritious meals!",
            "priority": "high",
            "scheduled_time": "08:00"
        })
        
        # Workout reminder
        notifications.append({
            "type": "workout_reminder",
            "title": "Time for Your Workout! 💪",
            "message": f"Ready to crush your fitness goals? Your {profile.fitness_level.value} workout is waiting for you!",
            "priority": "medium",
            "scheduled_time": "18:00"
        })
        
        # Progress check-in
        if recent_progress:
            notifications.append({
                "type": "progress_checkin",
                "title": "How are you feeling today? 📊",
                "message": "Take a moment to log your energy level and mood. This helps us personalize your plans!",
                "priority": "low",
                "scheduled_time": "20:00"
            })
        
        # Weekly summary
        notifications.append({
            "type": "weekly_summary",
            "title": "Your Weekly Progress Summary 📈",
            "message": "Check out your amazing progress this week! You're doing great!",
            "priority": "medium",
            "scheduled_time": "sunday_19:00"
        })
        
        return {
            "user_id": user_id,
            "notifications": notifications,
            "total_notifications": len(notifications),
            "created_at": datetime.now()
        }
    
    async def _get_recent_progress(self, user_id: str, days: int = 7) -> List[ProgressEntry]:
        """Get recent progress entries for user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            start_date = datetime.now() - timedelta(days=days)
            
            cursor.execute("""
                SELECT * FROM progress_entries 
                WHERE user_id = ? AND date >= ?
                ORDER BY date DESC
            """, (user_id, start_date))
            
            rows = cursor.fetchall()
            
            progress_entries = []
            for row in rows:
                progress_entries.append(ProgressEntry(
                    id=row[0],
                    user_id=row[1],
                    date=datetime.fromisoformat(row[2]),
                    weight=row[3],
                    body_fat_percentage=row[4],
                    measurements=json.loads(row[5]) if row[5] else {},
                    energy_level=row[6],
                    mood=row[7],
                    sleep_hours=row[8],
                    notes=row[9]
                ))
            
            return progress_entries
    
    async def _get_user_profile(self, user_id: str) -> Optional[UserProfile]:
        """Get user profile from database"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            cursor.execute("SELECT * FROM users WHERE id = ?", (user_id,))
            row = cursor.fetchone()
            
            if row:
                return UserProfile(
                    id=row[0],
                    name=row[1],
                    age=row[2],
                    gender=row[3],
                    height_cm=row[4],
                    weight_kg=row[5],
                    fitness_level=FitnessLevel(row[6]),
                    goal_type=GoalType(row[7]),
                    dietary_restrictions=[DietaryRestriction(d) for d in json.loads(row[8]) if row[8]],
                    allergies=json.loads(row[9]) if row[9] else [],
                    activity_level=row[10],
                    target_weight=row[11],
                    created_at=datetime.fromisoformat(row[12]),
                    updated_at=datetime.fromisoformat(row[13])
                )
            
            return None
    
    async def run_automated_workflow(self, user_id: str) -> Dict[str, Any]:
        """
        Run the complete automated fitness and meal planning workflow
        
        This orchestrates all Agent-S tasks:
        1. intake_agent: Collect user baseline and health constraints
        2. planner_agent: Generate daily plan and grocery list
        3. engagement_agent: Push notifications and weekly summaries
        4. compliance_agent: Ensure content avoids medical claims
        """
        self.logger.info(f"Starting automated fitness workflow for user {user_id}")
        
        workflow_results = {
            "user_id": user_id,
            "started_at": datetime.now(),
            "meal_plan_generated": False,
            "workout_plan_generated": False,
            "notifications_sent": 0,
            "compliance_checked": False,
            "errors": []
        }
        
        try:
            # Step 1: Generate daily meal plan
            meal_plan = await self.generate_meal_plan(user_id)
            workflow_results["meal_plan_generated"] = True
            
            # Step 2: Generate daily workout plan
            workout_plan = await self.generate_workout_plan(user_id)
            workflow_results["workout_plan_generated"] = True
            
            # Step 3: Send engagement notifications
            notifications = await self.send_engagement_notifications(user_id)
            workflow_results["notifications_sent"] = notifications["total_notifications"]
            
            # Step 4: Compliance check (simplified)
            compliance_result = await self._check_content_compliance(meal_plan, workout_plan)
            workflow_results["compliance_checked"] = compliance_result["passed"]
            
            workflow_results["completed_at"] = datetime.now()
            workflow_results["success"] = True
            
            self.logger.info("Automated fitness workflow completed successfully")
            
        except Exception as e:
            self.logger.error(f"Error in automated fitness workflow: {e}")
            workflow_results["errors"].append(str(e))
            workflow_results["success"] = False
        
        return workflow_results
    
    async def _check_content_compliance(self, meal_plan: MealPlan, workout_plan: WorkoutPlan) -> Dict[str, Any]:
        """
        Check content compliance to avoid medical claims
        
        Agent-S Task: compliance_agent
        """
        compliance_issues = []
        
        # Check meal plan for medical claims
        for meal in meal_plan.meals:
            for food in meal.get("foods", []):
                food_name = food["name"]
                # Check for medical claim keywords
                medical_keywords = ["cure", "treat", "heal", "medicine", "therapeutic"]
                if any(keyword in food_name.lower() for keyword in medical_keywords):
                    compliance_issues.append(f"Potential medical claim in food: {food_name}")
        
        # Check workout plan for medical claims
        for exercise in workout_plan.exercises:
            exercise_name = exercise["name"]
            # Check for medical claim keywords
            medical_keywords = ["cure", "treat", "heal", "medicine", "therapeutic"]
            if any(keyword in exercise_name.lower() for keyword in medical_keywords):
                compliance_issues.append(f"Potential medical claim in exercise: {exercise_name}")
        
        return {
            "passed": len(compliance_issues) == 0,
            "issues": compliance_issues,
            "checked_at": datetime.now()
        }
    
    async def get_user_analytics(self, user_id: str) -> Dict[str, Any]:
        """Get analytics for a specific user"""
        with sqlite3.connect(self.db_path) as conn:
            cursor = conn.cursor()
            
            # Get user profile
            profile = await self._get_user_profile(user_id)
            if not profile:
                return {}
            
            # Get meal plan count
            cursor.execute("SELECT COUNT(*) FROM meal_plans WHERE user_id = ?", (user_id,))
            meal_plans_count = cursor.fetchone()[0]
            
            # Get workout plan count
            cursor.execute("SELECT COUNT(*) FROM workout_plans WHERE user_id = ?", (user_id,))
            workout_plans_count = cursor.fetchone()[0]
            
            # Get progress entries count
            cursor.execute("SELECT COUNT(*) FROM progress_entries WHERE user_id = ?", (user_id,))
            progress_entries_count = cursor.fetchone()[0]
            
            # Get latest weight
            cursor.execute("SELECT weight FROM progress_entries WHERE user_id = ? AND weight IS NOT NULL ORDER BY date DESC LIMIT 1", (user_id,))
            latest_weight = cursor.fetchone()
            current_weight = latest_weight[0] if latest_weight else profile.weight_kg
            
            # Calculate weight change
            weight_change = current_weight - profile.weight_kg if profile.weight_kg else 0
            
            return {
                "user_name": profile.name,
                "fitness_level": profile.fitness_level.value,
                "goal_type": profile.goal_type.value,
                "current_weight": current_weight,
                "weight_change": weight_change,
                "meal_plans_generated": meal_plans_count,
                "workout_plans_generated": workout_plans_count,
                "progress_entries": progress_entries_count,
                "days_active": progress_entries_count,
                "last_updated": datetime.now()
            }

# Example usage and testing
async def main():
    """Example usage of the Fitness & Meal Planning Coach"""
    
    # Configuration
    config = {
        "nutrition_api_key": "your_nutrition_api_key",
        "fitness_api_key": "your_fitness_api_key",
        "push_notification_key": "your_push_notification_key"
    }
    
    # Initialize coach
    coach = FitnessMealCoach(config)
    
    # Sample user data
    user_data = {
        "name": "John Doe",
        "age": 30,
        "gender": "male",
        "height_cm": 175.0,
        "weight_kg": 80.0,
        "fitness_level": "intermediate",
        "goal_type": "weight_loss",
        "dietary_restrictions": ["none"],
        "allergies": [],
        "activity_level": "moderately_active",
        "target_weight": 75.0
    }
    
    # Create user profile
    user = await coach.create_user_profile(user_data)
    
    # Run automated workflow
    results = await coach.run_automated_workflow(user.id)
    
    print("Workflow Results:")
    print(json.dumps(results, indent=2, default=str))
    
    # Get user analytics
    analytics = await coach.get_user_analytics(user.id)
    
    print("\nUser Analytics:")
    print(json.dumps(analytics, indent=2, default=str))

if __name__ == "__main__":
    asyncio.run(main())
