/**
 * Conventional Portion Units Registry
 * Sourced directly from docta/data_pipeline/data/portion_units.json
 */
export const PORTION_UNITS_REGISTRY = {
  jollof_rice: {
    dish_id: "jollof_rice",
    dish_name: "Nigerian Jollof Rice",
    default_unit_id: "serving_spoon",
    default_quantity: 2.0,
    units: [
      {
        unit_id: "serving_spoon",
        unit_name: "Serving Spoon",
        gram_weight: 120.0,
        description: "Standard catering/cooking spoon (~120g)"
      },
      {
        unit_id: "mound_cup",
        unit_name: "Mound / Cup",
        gram_weight: 250.0,
        description: "Standard dining plate mound (~250g)"
      },
      {
        unit_id: "takeaway_pack",
        unit_name: "Takeaway Pack",
        gram_weight: 500.0,
        description: "Full standard plastic takeaway pack (~500g)"
      }
    ]
  },
  egusi_soup: {
    dish_id: "egusi_soup",
    dish_name: "Egusi Melon Seed Soup",
    default_unit_id: "serving_spoon",
    default_quantity: 2.0,
    units: [
      {
        unit_id: "serving_spoon",
        unit_name: "Serving Spoon",
        gram_weight: 100.0,
        description: "Standard cooking soup spoon (~100g)"
      },
      {
        unit_id: "small_bowl",
        unit_name: "Small Soup Bowl",
        gram_weight: 200.0,
        description: "Side soup bowl (~200g)"
      },
      {
        unit_id: "large_bowl",
        unit_name: "Large Soup Bowl",
        gram_weight: 350.0,
        description: "Main soup bowl (~350g)"
      }
    ]
  },
  amala: {
    dish_id: "amala",
    dish_name: "Amala (Yam Flour Swallow)",
    default_unit_id: "medium_wrap",
    default_quantity: 1.0,
    units: [
      {
        unit_id: "small_wrap",
        unit_name: "Small Wrap",
        gram_weight: 150.0,
        description: "Light portion wrap (~150g)"
      },
      {
        unit_id: "medium_wrap",
        unit_name: "Medium Wrap",
        gram_weight: 250.0,
        description: "Standard restaurant wrap (~250g)"
      },
      {
        unit_id: "large_wrap",
        unit_name: "Large Wrap",
        gram_weight: 400.0,
        description: "Heavy swallow portion (~400g)"
      }
    ]
  },
  fried_plantain: {
    dish_id: "fried_plantain",
    dish_name: "Fried Ripe Plantain (Dodo)",
    default_unit_id: "portion_6_slices",
    default_quantity: 1.0,
    units: [
      {
        unit_id: "single_slice",
        unit_name: "Single Slice / Piece",
        gram_weight: 25.0,
        description: "One slice (~25g)"
      },
      {
        unit_id: "portion_6_slices",
        unit_name: "Small Portion (6 slices)",
        gram_weight: 150.0,
        description: "Standard side portion (~150g)"
      },
      {
        unit_id: "large_portion",
        unit_name: "Large Portion (12 slices)",
        gram_weight: 300.0,
        description: "Double side portion (~300g)"
      }
    ]
  },
  moi_moi: {
    dish_id: "moi_moi",
    dish_name: "Steamed Bean Cake (Moi Moi)",
    default_unit_id: "single_wrap",
    default_quantity: 1.0,
    units: [
      {
        unit_id: "single_wrap",
        unit_name: "Single Wrap / Cup",
        gram_weight: 150.0,
        description: "Standard leaf or foil wrap (~150g)"
      },
      {
        unit_id: "large_wrap",
        unit_name: "Large Wrap",
        gram_weight: 250.0,
        description: "Large portion wrap (~250g)"
      }
    ]
  },
  pounded_yam: {
    dish_id: "pounded_yam",
    dish_name: "Pounded Yam (Iyan)",
    default_unit_id: "medium_wrap",
    default_quantity: 1.0,
    units: [
      {
        unit_id: "small_wrap",
        unit_name: "Small Wrap",
        gram_weight: 180.0,
        description: "Light wrap (~180g)"
      },
      {
        unit_id: "medium_wrap",
        unit_name: "Medium Wrap",
        gram_weight: 300.0,
        description: "Standard wrap (~300g)"
      },
      {
        unit_id: "large_wrap",
        unit_name: "Large Wrap",
        gram_weight: 450.0,
        description: "Hearty swallow portion (~450g)"
      }
    ]
  },
  suya: {
    dish_id: "suya",
    dish_name: "Beef Suya Skewers",
    default_unit_id: "skewer",
    default_quantity: 2.0,
    units: [
      {
        unit_id: "skewer",
        unit_name: "Stick / Skewer",
        gram_weight: 50.0,
        description: "Standard beef stick (~50g)"
      },
      {
        unit_id: "paper_wrap_small",
        unit_name: "Small Newspaper Wrap",
        gram_weight: 150.0,
        description: "Standard street portion (~150g)"
      },
      {
        unit_id: "paper_wrap_large",
        unit_name: "Large Newspaper Wrap",
        gram_weight: 300.0,
        description: "Generous sharing portion (~300g)"
      }
    ]
  }
};

export const GENERIC_DEFAULT_UNITS = [
  {
    unit_id: "standard_serving",
    unit_name: "Standard Serving",
    gram_weight: 150.0,
    description: "Standard medium portion (~150g)"
  },
  {
    unit_id: "large_serving",
    unit_name: "Large Serving",
    gram_weight: 300.0,
    description: "Double portion (~300g)"
  },
  {
    unit_id: "small_serving",
    unit_name: "Small Serving",
    gram_weight: 75.0,
    description: "Light side portion (~75g)"
  }
];

export const ALL_SUPPORTED_DISHES = [
  { id: "jollof_rice", name: "Nigerian Jollof Rice" },
  { id: "fried_plantain", name: "Fried Ripe Plantain (Dodo)" },
  { id: "egusi_soup", name: "Egusi Melon Seed Soup" },
  { id: "amala", name: "Amala (Yam Flour Swallow)" },
  { id: "moi_moi", name: "Steamed Bean Cake (Moi Moi)" },
  { id: "pounded_yam", name: "Pounded Yam (Iyan)" },
  { id: "suya", name: "Beef Suya Skewers" }
];
