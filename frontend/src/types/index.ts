export interface Tag {
  id: number;
  name: string;
  category: string | null;
}

export interface RecipeStep {
  id: number;
  step_number: number;
  instruction: string;
  image_url: string | null;
}

export interface RecipeIngredient {
  id: number;
  ingredient: { id: number; name: string; name_en: string | null };
  amount: string | null;
  unit: string | null;
  note: string | null;
  sort_order: number;
}

export interface RecipeSummary {
  id: number;
  title: string;
  description: string | null;
  servings: string | null;
  total_time: number | null;
  image_url: string | null;
  source_type: string | null;
  cooked_count: number;
  created_at: string;
  tags: Tag[];
}

export interface RecipeDetail extends RecipeSummary {
  source_url: string | null;
  notes: string | null;
  prep_time: number | null;
  cook_time: number | null;
  updated_at: string;
  steps: RecipeStep[];
  ingredients: RecipeIngredient[];
}

export interface ShoppingItem {
  id: number;
  name: string;
  is_checked: boolean;
  created_at: string;
}

export interface ScrapeResult {
  title: string | null;
  description: string | null;
  servings: string | null;
  prep_time: number | null;
  cook_time: number | null;
  total_time: number | null;
  image_url: string | null;
  source_url: string;
  source_type: string;
  steps: { step_number: number; instruction: string; image_url?: string }[];
  ingredients: { name: string; amount?: string; unit?: string; note?: string }[];
  suggested_tags: string[];
  scrape_success: boolean;
}
